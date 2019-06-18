from __future__ import print_function
import errno
import json
import os
import time
import uuid
import requests

from prominence import exceptions

def register_client():
    """
    Obtain a client id and secret from the OIDC provider
    """
    if os.path.isfile(os.path.expanduser('~/.prominence/client')):
        return True

    data = {}
    data['redirect_uris'] = ['%s/redirect_url' % os.environ['PROMINENCE_URL']]
    data['client_name'] = 'prominence-user-%s' % str(uuid.uuid4())
    data['token_endpoint_auth_method'] = 'client_secret_basic'
    data['scope'] = 'openid profile email'
    data['grant_types'] = ['urn:ietf:params:oauth:grant-type:device_code']
    data['response_types'] = ['code']

    # Create .prominence directory if necessary
    if not os.path.exists(os.path.expanduser('~/.prominence')):
        os.mkdir(os.path.expanduser('~/.prominence'))

    # Create OIDC client
    response = requests.post(os.environ['PROMINENCE_OIDC_URL']+'/register',
                             json=data,
                             timeout=10,
                             allow_redirects=True)

    if response.status_code == 201:
        with open(os.path.expanduser('~/.prominence/client'), 'w') as client_file:
            json.dump(response.json(), client_file)
        os.chmod(os.path.expanduser('~/.prominence/client'), 384)

        print('Client registration successful')
        return True
    
    raise exceptions.ClientRegistrationError('Client registration failed with status code %d' % response.status_code)

def authenticate_user(create_client_if_needed=True):
    """
    Obtain token from OIDC provider
    """
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

    response = requests.post(os.environ['PROMINENCE_OIDC_URL']+'/devicecode',
                             data=data,
                             timeout=10,
                             auth=(client_id, client_secret),
                             allow_redirects=True)

    if response.status_code == 401:
        raise exceptions.AuthenticationError('Unable to initiate the device code flow')

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
            response = requests.post(os.environ['PROMINENCE_OIDC_URL']+'/token',
                                     data=data,
                                     timeout=10,
                                     auth=(client_id, client_secret),
                                     allow_redirects=True)
        except requests.exceptions.RequestException:
            continue

        if response.status_code == 200:
            authenticated = True
            with open(os.path.expanduser('~/.prominence/token'), 'w') as token_file:
                json.dump(response.json(), token_file)
            os.chmod(os.path.expanduser('~/.prominence/token'), 384)
            print('Authentication successful')
            return True

    if not authenticated:
        raise exceptions.AuthenticationError('Authenication failed')

def get_client():
    """
    Load saved OIDC client details
    """
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
