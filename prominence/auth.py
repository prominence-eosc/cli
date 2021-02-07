from __future__ import print_function
import errno
import json
import jwt
import os
import time
import uuid
import requests

from prominence import exceptions

DEFAULT_PROMINENCE_URL = 'https://host-130-246-215-158.nubes.stfc.ac.uk/prominence/v1'
DEFAULT_PROMINENCE_OIDC_URL = 'https://host-130-246-215-158.nubes.stfc.ac.uk'

def create_config_dir():
    """
    Create the ~/.prominence directory
    """
    try:
        if not os.path.exists(os.path.expanduser('~/.prominence')):
            os.mkdir(os.path.expanduser('~/.prominence'))
    except IOError as err:
        raise exceptions.IOError(err)

def register_client():
    """
    Obtain a client id and secret from the OIDC provider
    """
    if os.path.isfile(os.path.expanduser('~/.prominence/client')):
        return True

    headers = {}
    headers['Content-type'] = 'application/json'

    data = {}
    data['redirect_uris'] = ['%s/redirect_url' % os.environ.get('PROMINENCE_URL', DEFAULT_PROMINENCE_URL)]
    data['client_name'] = 'prominence-user-%s' % str(uuid.uuid4())
    data['token_endpoint_auth_method'] = 'client_secret_basic'
    data['scope'] = 'openid profile email'
    data['grant_types'] = ['urn:ietf:params:oauth:grant-type:device_code']
    data['response_types'] = ['code']

    # Create .prominence directory if necessary
    create_config_dir()

    # Create OIDC client
    try:
        response = requests.post(os.environ.get('PROMINENCE_OIDC_URL', DEFAULT_PROMINENCE_OIDC_URL)+'/register',
                                 data=json.dumps(data),
                                 timeout=10,
                                 headers=headers,
                                 allow_redirects=True)
    except requests.exceptions.RequestException as err:
        raise exceptions.ClientRegistrationError(err)

    if response.status_code == 201:
        try:
            with open(os.path.expanduser('~/.prominence/client'), 'w') as client_file:
                json.dump(response.json(), client_file)
            os.chmod(os.path.expanduser('~/.prominence/client'), 384)
        except IOError as err:
            raise exceptions.ClientRegistrationError(err)

        print('Client registration successful')
        return True
    
    raise exceptions.ClientRegistrationError('Client registration failed with status code %d' % response.status_code)

def authenticate_user(create_client_if_needed=True, token_in_file=True):
    """
    Obtain token from OIDC provider
    """
    # Create .prominence directory if necessary: this is done automatically if the user registers as a client, but for
    # the case of reading the client credentials from environment variables this step will be missed
    create_config_dir()

    try:
        (client_id, client_secret) = get_client()
    except exceptions.ClientCredentialsError:
        client_id = None

    if not client_id:
        if create_client_if_needed:
            if register_client():
                (client_id, client_secret) = get_client()
                if not client_id:
                    raise exceptions.ClientCredentialsError('Unable to get a client id and client secret')
            else:
                raise exceptions.ClientCredentialsError('Unable to get a client id and client secret')
        else:
            raise exceptions.ClientCredentialsError('Unable to get a client id and client secret, and automatic registration was disabled')

    data = {}
    data['scope'] = 'openid profile email'
    data['client_id'] = client_id

    try:
        response = requests.post(os.environ.get('PROMINENCE_OIDC_URL', DEFAULT_PROMINENCE_OIDC_URL)+'/devicecode',
                                 data=data,
                                 timeout=10,
                                 auth=(client_id, client_secret),
                                 allow_redirects=True)
    except requests.exceptions.RequestException as err:
        raise exceptions.AuthenticationError('Unable to initiate the device code flow: cannot connect to OIDC server')

    if response.status_code != 200:
        raise exceptions.AuthenticationError('Unable to initiate the device code flow: got status code %d' % response.status_code)

    device_code_response = response.json()

    print('To obtain a token, use a web browser to open the page %s and enter the code %s when requested' % (device_code_response['verification_uri'], device_code_response['user_code']))

    data = {}
    data['grant_type'] = 'urn:ietf:params:oauth:grant-type:device_code'
    data['device_code'] = device_code_response['device_code']

    # Wait for the user to authenticate
    current_time = time.time()
    authenticated = False
    while time.time() < current_time + int(device_code_response['expires_in']) and not authenticated:
        time.sleep(5)
        try:
            response = requests.post(os.environ.get('PROMINENCE_OIDC_URL', DEFAULT_PROMINENCE_OIDC_URL)+'/token',
                                     data=data,
                                     timeout=10,
                                     auth=(client_id, client_secret),
                                     allow_redirects=True)
        except requests.exceptions.RequestException:
            continue

        if response.status_code == 200:
            authenticated = True
            if token_in_file:
                try:
                    with open(os.path.expanduser('~/.prominence/token'), 'w') as token_file:
                        json.dump(response.json(), token_file)
                    os.chmod(os.path.expanduser('~/.prominence/token'), 384)
                except IOError:
                    raise exceptions.AuthenticationError('Unable to write to ~/.prominence/token')
            else:
                return response.json()['access_token']

    if not authenticated:
        raise exceptions.AuthenticationError('Authentication failed')

    return True

def get_client():
    """
    Load saved OIDC client details
    """
    if 'PROMINENCE_OIDC_CLIENT_ID' in os.environ and 'PROMINENCE_OIDC_CLIENT_SECRET' in os.environ:
        return (os.environ['PROMINENCE_OIDC_CLIENT_ID'], os.environ['PROMINENCE_OIDC_CLIENT_SECRET'])

    if os.path.isfile(os.path.expanduser('~/.prominence/client')):
        with open(os.path.expanduser('~/.prominence/client')) as json_data:
            data = json.load(json_data)

        if 'client_id' in data and 'client_secret' in data:
            return (data['client_id'], data['client_secret'])
        else:
            raise exceptions.ClientCredentialsError('The saved OIDC client file is invalid')

    raise exceptions.ClientCredentialsError('The file ~/.prominence/client does not exist')

def get_token():
    """
    Load saved token
    """
    if os.path.isfile(os.path.expanduser('~/.prominence/token')):
        with open(os.path.expanduser('~/.prominence/token')) as json_data:
            data = json.load(json_data)

        if 'access_token' in data:
            return data['access_token']
        else:
            raise exceptions.TokenError('The saved token file does not contain access_token')
    raise exceptions.TokenError('The file ~/.prominence/token does not exist')

def get_expiry(token):
    """
    Get expiry date from a JWT token
    """
    expiry = 0
    try:
        expiry = jwt.decode(token, options={"verify_signature": False})['exp']
    except:
        pass
    return expiry
