from __future__ import print_function
import argparse
import base64
from collections import OrderedDict
import errno
import json
import os
import re
import shlex
import shutil
from string import Template
import sys
import time
import requests
import yaml
import uuid

from prominence import auth
from prominence import exceptions
from prominence import __version__
from prominence import ProminenceClient

CMD_MAX_WIDTH = 100

def handle_multiline_commands(job):
    """
    If cmd contains new lines, split into multiple tasks or a single task
    with an input file
    """
    new_tasks = []
    for task in job['tasks']:
        if 'cmd' not in task:
            new_tasks.append(task)
        elif '\n' not in task['cmd']:
            new_tasks.append(task)
        elif task['cmd'].startswith('#!'):
            executable = str(uuid.uuid4())
            inputs = []
            if 'inputs' in job:
                inputs = job['inputs']
            inputs.append({'filename': executable,
                           'content': base64.b64encode(task['cmd'].encode()).decode("utf-8"),
                           'executable': True})
            task['cmd'] = './%s' % executable
            job['inputs'] = inputs
            new_tasks.append(task)
        else:
            for command in task['cmd'].split('\n'):
                if command != '':
                    new_task = task.copy()
                    new_task['cmd'] = command
                    new_tasks.append(new_task)
    job['tasks'] = new_tasks
    return job

def elapsed(job):
    """
    Print elapsed job runtime in a nice way
    """
    if 'startTime' in job['events']:
        if 'endTime' in job['events']:
            elapsed_time = job['events']['endTime'] - job['events']['startTime']
        else:
            elapsed_time = time.time() - job['events']['startTime']
        days = int(elapsed_time/86400)
        time_fmt = '%H:%M:%S'
        return '%d+%s' % (days, time.strftime(time_fmt, time.gmtime(elapsed_time)))

    return ''

def datetime_format(epoch):
    """
    Convert a unix epoch in a formatted date/time string
    """
    datetime_fmt = '%Y-%m-%d %H:%M:%S'
    return time.strftime(datetime_fmt, time.gmtime(epoch))

def print_json(content, transform=False, detail=False, resource='job'):
    """
    Print JSON in a nice way
    """
    if transform:
        if isinstance(content, list):
            content = transform_item_list(content, detail, resource)
        else:
            content = transform_item(content, detail, resource)
    print(json.dumps(content, indent=2))

def image_name(name):
    """
    Extract container image name for display purposes
    """
    if name.startswith('http'):
        name = os.path.basename(name)
        name = name[:name.find('?')]
    return name

def list_jobs(jobs):
    """
    Print list of jobs
    """
    width_id = 2
    width_name = 4
    width_created = 19
    width_status = 6
    width_elapsed = 10
    width_container = 5
    width_cmd = 3

    for job in jobs:
        my_cmd = ''
        if 'cmd' in job['tasks'][0]:
            my_cmd = job['tasks'][0]['cmd']
        my_name = ''
        if 'name' in job:
            my_name = job['name']

        width_id_current = len(str(job['id']))
        width_name_current = len(my_name)
        width_status_current = len(job['status'])
        width_container_current = len(image_name(job['tasks'][0]['image']))
        width_cmd_current = len(my_cmd)

        if width_cmd_current > CMD_MAX_WIDTH:
            width_cmd_current = CMD_MAX_WIDTH + 3
            my_cmd = '%s...' % my_cmd[0:CMD_MAX_WIDTH]

        if width_id_current > width_id:
            width_id = width_id_current
        if width_name_current > width_name:
            width_name = width_name_current
        if width_status_current > width_status:
            width_status = width_status_current
        if width_container_current > width_container:
            width_container = width_container_current
        if width_cmd_current > width_cmd:
            width_cmd = width_cmd_current

    print('%s   %s   %s   %s   %s   %s   %s' % ('ID'.ljust(width_id),
                                                'NAME'.ljust(width_name),
                                                'CREATED'.ljust(width_created),
                                                'STATUS'.ljust(width_status),
                                                'ELAPSED'.ljust(width_elapsed),
                                                'IMAGE'.ljust(width_container),
                                                'CMD'.ljust(width_cmd)))

    for job in jobs:
        my_cmd = ''
        if 'cmd' in job['tasks'][0]:
            my_cmd = job['tasks'][0]['cmd']
            if len(my_cmd) > CMD_MAX_WIDTH:
                my_cmd = '%s...' % my_cmd[0:CMD_MAX_WIDTH]
        my_name = ''
        if 'name' in job:
            my_name = job['name']
        print('%s   %s   %s   %s   %s   %s   %s' % (str(job['id']).ljust(width_id),
                                                    my_name.ljust(width_name),
                                                    datetime_format(job['events']['createTime']).ljust(width_created),
                                                    job['status'].ljust(width_status),
                                                    elapsed(job).ljust(width_elapsed),
                                                    image_name(job['tasks'][0]['image']).ljust(width_container),
                                                    my_cmd.ljust(width_cmd)))

def list_workflows(workflows):
    """
    Print list of workflows
    """
    width_id = 2
    width_name = 4
    width_created = 19
    width_status = 6
    width_elapsed = 10
    width_success = 8
    width_failed = 8
    width_total = 8

    for workflow in workflows:
        width_id_current = len(str(workflow['id']))
        width_name_current = len(workflow['name'])
        width_status_current = len(workflow['status'])
        width_success_current = len('%d' % workflow['progress']['done'])
        width_failed_current = len('%d' % workflow['progress']['failed'])
        width_total_current = len('%d' % workflow['progress']['total'])

        if width_id_current > width_id:
            width_id = width_id_current
        if width_name_current > width_name:
            width_name = width_name_current
        if width_status_current > width_status:
            width_status = width_status_current
        if width_success_current > width_success:
            width_success = width_success_current
        if width_failed_current > width_failed:
            width_failed = width_failed_current
        if width_total_current > width_total:
            width_total = width_total_current

    print('%s   %s   %s   %s   %s   %s   %s   %s' % ('ID'.ljust(width_id),
                                                     'NAME'.ljust(width_name),
                                                     'CREATED'.ljust(width_created),
                                                     'STATUS'.ljust(width_status),
                                                     'ELAPSED'.ljust(width_elapsed),
                                                     'SUCCESS'.ljust(width_success),
                                                     'FAILED'.ljust(width_failed),
                                                     'TOTAL'.ljust(width_total)))

    for workflow in workflows:
        print('%s   %s   %s   %s   %s   %s   %s   %s' % (str(workflow['id']).ljust(width_id),
                                                         workflow['name'].ljust(width_name),
                                                         datetime_format(workflow['events']['createTime']).ljust(width_created),
                                                         workflow['status'].ljust(width_status),
                                                         elapsed(workflow).ljust(width_elapsed),
                                                         ('%d' % workflow['progress']['done']).ljust(width_success),
                                                         ('%d' % workflow['progress']['failed']).ljust(width_failed),
                                                         ('%d' % workflow['progress']['total']).ljust(width_total)))

def transform_job(job, detail):
    """
    Transform a job into the required format for printing
    """
    job_t = OrderedDict()
    job_t['id'] = job['id']
    if 'name' in job:
        if job['name'] != '' or not detail:
            job_t['name'] = job['name']

    job_t['status'] = job['status']

    if detail and 'statusReason' in job:
        job_t['statusReason'] = job['statusReason']

    if detail:
        if 'storage' in job:
            job_t['storage'] = job['storage']
        job_t['resources'] = job['resources']
        if 'labels' in job:
            job_t['labels'] = job['labels']
        if 'artifacts' in job:
            job_t['artifacts'] = job['artifacts']
        if 'inputFiles' in job:
            job_t['inputFiles'] = job['inputFiles']
        if 'outputFiles' in job:
            job_t['outputFiles'] = job['outputFiles']
        if 'outputDirs' in job:
            job_t['outputDirs'] = job['outputDirs']
        if 'parameters' in job:
            job_t['parameters'] = job['parameters']

    job_t['tasks'] = job['tasks']

    if detail:
        if 'policies' in job:
            job_t['policies'] = job['policies']
        if 'notifications' in job:
            job_t['notifications'] = job['notifications']

    events = OrderedDict()
    if 'events' in job:
        if 'createTime' in job['events']:
            if detail:
                events['createTime'] = datetime_format(job['events']['createTime'])
            else:
                events['createTime'] = job['events']['createTime']

    if 'startTime' in job['events']:
        if detail:
            events['startTime'] = datetime_format(job['events']['startTime'])
        else:
            events['startTime'] = job['events']['startTime']
    if 'endTime' in job['events']:
        if detail:
            events['endTime'] = datetime_format(job['events']['endTime'])
        else:
            events['endTime'] = job['events']['endTime']
    job_t['events'] = events

    execution = OrderedDict()
    if 'execution' in job:
        if 'site' in job['execution']:
            execution['site'] = job['execution']['site']
        if 'provisionedResources' in job['execution']:
            execution['provisionedResources'] = job['execution']['provisionedResources']
        if 'cpu' in job['execution']:
            execution['cpu'] = job['execution']['cpu']
        if 'runtimeVersion' in job['execution']:
            execution['runtimeVersion'] = job['execution']['runtimeVersion']
        if 'maxMemoryUsageKB' in job['execution']:
            execution['maxMemoryUsageKB'] = job['execution']['maxMemoryUsageKB']
        if 'stageInTime' in job['execution']:
            execution['stageInTime'] = job['execution']['stageInTime']
        if 'stageOutTime' in job['execution']:
            execution['stageOutTime'] = job['execution']['stageOutTime']
        if 'retries' in job['execution']:
            execution['retries'] = job['execution']['retries']
        if 'tasks' in job['execution']:
            tasks = []
            for task in job['execution']['tasks']:
                task_t = {}
                if 'exitCode' in task:
                    task_t['exitCode'] = task['exitCode']
                if 'retries' in task:
                    task_t['retries'] = task['retries']
                if 'imagePullTime' in task:
                    task_t['imagePullTime'] = float('%.4g' % task['imagePullTime'])
                if 'imageSha256' in task:
                    task_t['imageSha256'] = task['imageSha256']
                if 'wallTimeUsage' in task:
                    task_t['wallTimeUsage'] = float('%.4g' % task['wallTimeUsage'])
                if 'cpuTimeUsage' in task:
                    task_t['cpuTimeUsage'] = float('%.4g' % task['cpuTimeUsage'])
                if 'maxResidentSetSizeKB' in task:
                    task_t['maxResidentSetSizeKB'] = task['maxResidentSetSizeKB']
                tasks.append(task_t)

            execution['tasks'] = tasks
        job_t['execution'] = execution

    return job_t

def transform_workflow(workflow, detail):
    """
    Transform a workflow into the required format for printing
    """
    workflow_t = OrderedDict()
    workflow_t['id'] = workflow['id']
    if workflow['name'] != '' or not detail:
        workflow_t['name'] = workflow['name']

    workflow_t['status'] = workflow['status']

    if detail and 'statusReason' in workflow:
        workflow_t['statusReason'] = workflow['statusReason']

    if detail:
        if 'storage' in workflow:
            workflow_t['storage'] = workflow['storage']
        workflow_t['jobs'] = workflow['jobs']
        if 'dependencies' in workflow:
            workflow_t['dependencies'] = workflow['dependencies']
        if 'factory' in workflow:
            workflow_t['factory'] = workflow['factory']

    events = OrderedDict()
    if 'events' in workflow:
        if 'createTime' in workflow['events']:
            if detail:
                events['createTime'] = datetime_format(workflow['events']['createTime'])
            else:
                events['createTime'] = workflow['events']['createTime']

    if 'startTime' in workflow['events']:
        if detail:
            events['startTime'] = datetime_format(workflow['events']['startTime'])
        else:
            events['startTime'] = workflow['events']['startTime']
    if 'endTime' in workflow['events']:
        if detail:
            events['endTime'] = datetime_format(workflow['events']['endTime'])
        else:
            events['endTime'] = workflow['events']['endTime']
    workflow_t['events'] = events

    if 'progress' in workflow:
        workflow_t['progress'] = workflow['progress']

    return workflow_t

def transform_item(data, detail, resource):
    """
    Transform a job/workflow into the required format ordered by id
    """
    if 'job' in resource:
        return transform_job(data, detail)
    else:
        return transform_workflow(data, detail)

def transform_item_list(result, detail, resource):
    """
    Transform a job/workflow list into the required format ordered by id
    """
    if 'job' in resource:
        items = [transform_job(job, detail) for job in result]
    else:
        items = [transform_workflow(workflow, detail) for workflow in result]
    return sorted(items, key=lambda k: int(k['id']))

def command_register(args):
    """
    Obtain a client id and secret from the OIDC provider
    """
    try:
        auth.register_client()
    except exceptions.ClientRegistrationError as err:
        print('Error:', err)
        exit(1)

def command_login(args):
    """
    Obtain token from OIDC provider
    """
    try:
        if auth.authenticate_user(create_client_if_needed=False, token_in_file=True):
            print('Successfully retrieved token')
    except exceptions.ClientCredentialsError as err:
        print('Error:', err)
        exit(1)
    except exceptions.AuthenticationError as err:
        print('Error:', err)
        exit(1)

def command_list(args):
    """
    List running/idle or completed jobs or workflows
    """
    status = None
    if args.completed:
        status = 'completed'
    if args.all:
        status = 'all'
    if args.running:
        status = 'running'
    if args.idle:
        status = 'idle'
    num = 1
    if args.num:
        num = args.num
    constraint = None
    if args.constraint:
        constraint = args.constraint
    name_constraint = None
    if args.name:
        name_constraint = args.name

    workflow = None
    if args.id:
        workflow = args.id

    try:
        client = ProminenceClient(authenticated=True)
        if args.resource == 'jobs':
            data = client.list_jobs(status, num, constraint, name_constraint, workflow)
        else:
            data = client.list_workflows(status, num, constraint, name_constraint)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.JobGetError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    if args.resource == 'jobs':
        list_jobs(transform_item_list(data, False, 'job'))
    else:
        list_workflows(transform_item_list(data, False, 'workflow'))

def command_exec(args):
    """
    Execute a command inside a running job
    """
    try:
        client = ProminenceClient(authenticated=True)
        output = client.execute_command(args.id, shlex.split(str(args.command)))
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except exceptions.ExecError as err:
        print('Error: Unable to execute command:', err)
        exit(1)
    except Exception as err:
        print('Error:', err)
        exit(1)

    print(output)

def command_snapshot(args):
    """
    Create a snapshot of a file or directory in a running job and download it
    """
    print('Creating snapshot...')
    try:
        client = ProminenceClient(authenticated=True)
        output = client.create_snapshot(args.id, args.path)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except exceptions.SnapshotCreateError as err:
        print('Error: Unable to create snapshot:', err)
        exit(1)
    except Exception as err:
        print('Error:', err)
        exit(1)

    try:
        client = ProminenceClient(authenticated=True)
        data = client.get_snapshot_url(args.id)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except exceptions.SnapshotGetError as err:
        print('Error: Unable to get snapshot:', err)
        exit(1)
    except Exception as err:
        print('Error:', err)
        exit(1)

    if 'url' in data:
        url = data['url']
    else:
        print('Error: URL of snapshot not available')
        exit(1)

    try:
        response = requests.get(url, stream=True, timeout=30)
    except requests.exceptions.RequestException as err:
        print('Error getting file due to: %s' % err)
        exit(1)

    total_length = response.headers.get('content-length')

    if response.status_code != 200:
        print('Error: content from file/directory "%s" does not exist' % args.path)
        exit(1)

    with open('snapshot.tgz', 'wb') as file_download:
        print('Downloading file "snapshot.tgz"')
        if total_length is None:
            file_download.write(response.content)
        else:
            downloaded = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                downloaded += len(data)
                file_download.write(data)
                done = int(50 * downloaded / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
                sys.stdout.flush()
    print('')

def command_describe(args):
    """
    Describe a specific job or workflow
    """
    try:
        client = ProminenceClient(authenticated=True)
        if args.resource == 'job':
            data = client.describe_job(args.id)
        else:
            data = client.describe_workflow(args.id)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.JobGetError, exceptions.ConnectionError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    print_json(data, transform=True, detail=True, resource=args.resource)

def command_upload(args):
    """
    Upload a file to transient storage
    """
    if args.name is None:
        print('Error: a name must be specified')
        exit(1)
    if args.filename is None:
        print('Error: a filename must be specified')
        exit(1)

    try:
        client = ProminenceClient(authenticated=True)
        response = client.upload(args.name, args.filename, args.checksum)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.FileUploadError, exceptions.ConnectionError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    print('Success')

def command_download(args):
    """
    Download output files and directories
    """
    jobs = []
    try:
        client = ProminenceClient(authenticated=True)
        if args.resource == 'job':
            jobs.append(client.describe_job(args.id))
        else:
            jobs = client.list_jobs('completed', 1, '', '', args.id, True)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.JobGetError, exceptions.ConnectionError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    for job in jobs:
        if args.resource == 'workflow':
            print('Working on job %d' % job['id'])
        if ('outputFiles' in job or 'outputDirs' in job) and job['status'] in ('completed', 'failed', 'deleted'):
            # Create per-job directory if necessary & set path for files
            path = './'
            if args.dir:
                path = './%d/' % job['id']
                try:
                    os.mkdir(path)
                except OSError as err:
                    if err.errno != errno.EEXIST:
                        print('Error: job directory cannot be created')
                        exit(1)
                    else:
                        pass

            files_and_dirs = []
            if 'outputFiles' in job:
                files_and_dirs += job['outputFiles']
            if 'outputDirs' in job:
                files_and_dirs += job['outputDirs']

            for pair in files_and_dirs:
                file_name = os.path.basename(pair['name'])
                if 'outputDirs' in job:
                    if pair in job['outputDirs']:
                        file_name = file_name + '.tgz'
                file_name_orig = file_name

                if 'parameters' in job:
                    for parameter in job['parameters']:
                        file_name = Template(file_name).safe_substitute({parameter:job['parameters'][parameter]})

                url = pair['url']

                if os.path.isfile(path + file_name) and not args.force:
                    print('Warning: file "%s" already exists and force option not specified' % file_name)
                    continue

                if url == '':
                    print('Warning: no URL available for "%s"' % pair['name'])
                    continue

                try:
                    response = requests.get(url, stream=True, timeout=30)
                except requests.exceptions.RequestException as err:
                    print('Error getting file due to: %s' % err)
                    continue

                total_length = response.headers.get('content-length')

                if response.status_code != 200:
                    print('Error: content from file "%s" does not exist' % file_name)
                    continue

                with open(path + file_name, 'wb') as file_download:
                    print('Downloading file %s as %s' % (file_name_orig, file_name))
                    if total_length is None:
                        file_download.write(response.content)
                    else:
                        downloaded = 0
                        total_length = int(total_length)
                        for data in response.iter_content(chunk_size=4096):
                            downloaded += len(data)
                            file_download.write(data)
                            done = int(50 * downloaded / total_length)
                            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
                            sys.stdout.flush()
                print('')

def command_ls(args):
    """
    List objects in cloud storage
    """
    path = None
    if args.path:
        path = args.path

    try:
        client = ProminenceClient(authenticated=True)
        objects = client.list_objects(path)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.ObjectError) as err:
        print('Error:', err)
        exit(1)

    if objects:
        p1 = max([len('%d' % obj['size']) for obj in objects])
        p2 = max([len('%s' % obj['lastModified']) for obj in objects])
        p3 = max([len('%s' % obj['name']) for obj in objects])

        for object in objects:
            if args.long:
                print(object['name'].ljust(p3), ' ', ('%d' % object['size']).rjust(p1), ' ', object['lastModified'].rjust(p2))
            else:
                print(object['name'])


def command_rm(args):
    """
    Delete an object in cloud storage
    """
    if not args.object:
        print('Error: an object name must be specified')
        exit(1)

    try:
        client = ProminenceClient(authenticated=True)
        client.delete_object(args.object)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.ObjectError) as err:
        print('Error:', err)
        exit(1)

    print('Success')

def command_remove(args):
    """
    Remove a job or workflow from the queue
    """
    try:
        client = ProminenceClient(authenticated=True)
        client.remove(args.resource, args.id)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.RemoveFromQueueError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    if args.resource == 'workflow':
        print('Workflow removed from queue')
    else:
        print('Job removed from queue')

def command_delete(args):
    """
    Delete a job or workflow
    """
    try:
        client = ProminenceClient(authenticated=True)
        if args.resource == 'job':
            client.delete_job(args.id)
        else:
            client.delete_workflow(args.id)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.DeletionError) as err:
        print('Error:', err)
        exit(1)

    print('Success')

def command_stdout(args):
    """
    Get standard output for a specific job/workflow
    """
    try:
        client = ProminenceClient(authenticated=True)
        if args.job:
            print(client.stdout_workflow(args.id, args.job, args.node, args.instance))
        elif args.job:
            print(client.stdout_workflow(args.id, args.job, args.node))
        else:
            print(client.stdout_job(args.id, args.node))
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.StdStreamsError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

def command_stderr(args):
    """
    Get standard error for a specific job/workflow
    """
    try:
        client = ProminenceClient(authenticated=True)
        if args.job:
            print(client.stderr_workflow(args.id, args.job, args.node, args.instance))
        elif args.job:
            print(client.stderr_workflow(args.id, args.job, args.node))
        else:
            print(client.stderr_job(args.id, args.node))
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.StdStreamsError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

def command_rerun(args):
    """
    Re-run any failed jobs from a completed workflow
    """
    try:
        client = ProminenceClient(authenticated=True)
        resource_id = client.rerun(args.id)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.JobCreationError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    print('Workflow created with id %d' % resource_id)

def command_clone(args):
    """
    Clone a job or workflow
    """
    try:
        client = ProminenceClient(authenticated=True)
        resource_id = client.clone(args.resource, args.id)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.JobCreationError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    if args.resource == 'workflow':
        print('Workflow created with id %d' % resource_id)
    else:
        print('Job created with id %d' % resource_id)

def command_run(args):
    """
    Create a job from a JSON file, YAML file or URL
    """
    if args.file.startswith('http://') or args.file.startswith('https://'):
        try:
            response = requests.get(args.file)
        except requests.exceptions.RequestException as err:
            print('Error getting URL due to: %s' % err)
            exit(1)
        if response.status_code == 200:
            try:
                data = response.json()
            except json.decoder.JSONDecodeError as err:
                print('Error: problem with JSON at URL: %s' % err)
                exit(1)
        else:
            print('Error: got status %d from URL with message: %s' % (response.status_code, response.text))
            exit(1)
    else:
        try:
            with open(args.file) as json_file:
                data = json.load(json_file)
        except json.decoder.JSONDecodeError:
            try:
                with open(args.file) as yaml_file:
                    data = yaml.safe_load(yaml_file)
            except Exception as err:
                print('Error: %s' % err)
                exit(1)
        except (IOError, ValueError) as err:
            print('Error: %s' % err)
            exit(1)

    # Handle multi-line cmd
    if 'jobs' in data:
        for job in data['jobs']:
            job = handle_multiline_commands(job)
    else:
        data = handle_multiline_commands(data)

    # If filenames are specified as inputs, replace with content
    if 'inputs' in data:
        new_inputs = []
        for item in data['inputs']:
            if not isinstance(item, dict):
                if item.startswith('file://'):
                    filename = item.replace('file://', '')
                    if os.path.isfile(filename):
                        if os.path.getsize(filename) < 1000000:
                            with open(filename, 'rb') as input_file:
                                new_inputs.append({'filename':os.path.basename(filename),
                                                   'content':base64.b64encode(input_file.read()).decode("utf-8")})
                        else:
                            print('Error: Input file size too large')
                            exit(1)
            else:
                new_inputs.append(item)
        if new_inputs:
            data['inputs'] = new_inputs

    if 'jobs' in data:
        new_jobs = []
        for job in data['jobs']:
            if 'inputs' in job:
                new_inputs = []
                for item in job['inputs']:
                    if not isinstance(item, dict):
                        if item.startswith('file://'):
                            filename = item.replace('file://', '')
                            if os.path.isfile(filename):
                                if os.path.getsize(filename) < 1000000:
                                    with open(filename, 'rb') as input_file:
                                        new_inputs.append({'filename':os.path.basename(filename),
                                                           'content':base64.b64encode(input_file.read()).decode("utf-8")})
                                else:
                                    print('Error: Input file size too large')
                                    exit(1)
                    else:
                        new_inputs.append(item)
                if new_inputs:
                    job['inputs'] = new_inputs
            new_jobs.append(job)
        data['jobs'] = new_jobs

    try:
        client = ProminenceClient(authenticated=True)
        if 'jobs' in data:
            res_id = client.create_workflow(data)
            resource = 'Workflow'
        else:
            res_id = client.create_job(data)
            resource = 'Job'
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.JobCreationError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    print('%s created with id %d' % (resource, res_id))

def command_create(args):
    """
    Create a job
    """
    resources = {}
    if not args.totalcpusrange:
        resources['nodes'] = args.nodes
    resources['disk'] = args.disk
    if args.walltime:
        resources['walltime'] = args.walltime

    if args.cpusrange and args.cpusoptions:
        print('Error: do not specify both --cpus-range and --cpus-options')
        exit(1)

    if args.nodes > 1 and args.totalcpusrange:
        print('Error: do not specify both --nodes and --total-cpus-range')
        exit(1)

    if args.cpusrange:
        match = re.search(r'\d+\,\d+', args.cpusrange)
        if not match:
            print('Error: --cpus-range must be in the form "min,max" where min and max are integers')
            exit(1)
        resources['cpusRange'] = [int(x) for x in args.cpusrange.split(',')]
    elif args.cpusoptions:
        match = re.search(r'\d+\,\d+', args.cpusoptions)
        if not match:
            print('Error: --cpus-options must be in the form "x,y" where x and y are integers')
            exit(1)
        resources['cpusOptions'] = [int(x) for x in args.cpusoptions.split(',')]
    else:
        resources['cpus'] = args.cpus

    if args.totalcpusrange:
        match = re.search(r'\d+\,\d+', args.totalcpusrange)
        if not match:
            print('Error: --total-cpus-range must be in the form "min,max" where min and max are integers')
            exit(1)
        resources['totalCpusRange'] = [int(x) for x in args.totalcpusrange.split(',')]

    if args.memorypercpu:
        resources['memoryPerCpu'] = args.memorypercpu
    else:
        resources['memory'] = args.memory

    job = {}
    job['resources'] = resources
    job['name'] = args.name

    task = {}
    task['image'] = args.image

    user_env = []
    if args.env:
        user_env = args.env

    # MPI processes per node
    if args.openmpi or args.mpich or args.intelmpi:
        if args.ppn > 0:
            task['procsPerNode'] = args.ppn

        if args.ompppn > 0 and args.ppn > 0:
            print('Error: do not specify both --procs-per-node and --openmp-procs-per-node')
            exit(1)
        elif args.ompppn > 0 and args.ppn == 0:
            task['procsPerNode'] = job['resources']['cpus'] - args.ompppn
            user_env.append('OMP_NUM_THREADS=%d' % args.ompppn)

    # Working directory
    if args.workdir:
        task['workdir'] = args.workdir

    # Container runtime - use singularity by default but use udocker if the user has
    # specified a tarball using a URL
    if args.runtime:
        task['runtime'] = args.runtime
    else:
        if re.match(r'^http', args.image) and ('.tar' in args.image or '.tgz' in args.image):
            task['runtime'] = 'udocker'
        else:
            task['runtime'] = 'singularity'

    # Job type
    if args.openmpi:
        task['type'] = 'openmpi'
    elif args.mpich:
        task['type'] = 'mpich'
    elif args.intelmpi:
        task['type'] = 'intelmpi'

    # If multiple nodes are specified need to specify MPI type
    if 'nodes' in job['resources']:
        if job['resources']['nodes'] > 1 and 'type' not in task:
            print('Error: more than one node has been requested but MPI has not been specified')
            exit(1)

    if 'totalCpuRange' in job['resources'] and 'type' not in task:
        print('Error: more than one node may have been requested but MPI has not been specified')
        exit(1)

    # Optional command to run
    if args.command:
        task['cmd'] = args.command

    # Output files
    if args.outputfile:
        job['outputFiles'] = args.outputfile

    # Output directories
    if args.outputdir:
        job['outputDirs'] = args.outputdir

    # Files to be fetched
    if args.artifact:
        job['artifacts'] = []
        for file in args.artifact:
            artifact = {}
            artifact['url'] = file
            if (':' in file and ('http:' not in file or ('http:' in file and file.count(':') > 1)) \
                            and ('https:' not in file or ('https:' in file and file.count(':') > 1))):
                artifact['url'] = file.split(':')[0]
                artifact['mountpoint'] = '%s:%s' % (file.split(':')[1], file.split(':')[2])
            else:
                artifact['url'] = file
            job['artifacts'].append(artifact)

    # Automatically transfer contents of specified directory to job
    tarball = str(uuid.uuid4())
    if args.directory:
        if 'artifacts' not in job:
            job['artifacts'] = []
        try:
            shutil.make_archive('/tmp/%s' % tarball, 'gztar', args.directory)
        except Exception as err:
            print('Error: Unable to create directory tarball:', err)
            exit(1)
        job['artifacts'].append({'url': '%s.tar.gz' % tarball})

        try:
            client = ProminenceClient(authenticated=True)
            response = client.upload('%s.tar.gz' % tarball, '/tmp/%s.tar.gz' % tarball)
        except exceptions.AuthenticationError:
            print('Error: authentication failed')
            exit(1)
        except exceptions.TokenExpiredError:
            print('Error: access token has expired')
            exit(1)
        except (exceptions.FileUploadError, exceptions.ConnectionError, exceptions.TokenError) as err:
            print('Error:', err)
            exit(1)

    # Files to be uploaded
    if args.inputfile:
        inputs = []
        for filename in args.inputfile:
            if os.path.isfile(filename):
                if os.path.getsize(filename) < 1000000:
                    with open(filename, 'rb') as input_file:
                        inputs.append({'filename':os.path.basename(filename),
                                       'content':base64.b64encode(input_file.read()).decode("utf-8")})
                else:
                    print('Error: Input file size too large')
                    exit(1)
            else:
                print('Error: File "%s" does not exist' % filename)
                exit(1)
        job['inputs'] = inputs

    # Environment variables
    if user_env:
        env = {}
        for pair in user_env:
            if '=' in pair:
                items = pair.split('=')
                env[items[0]] = items[1]
        task['env'] = env

    # Metadata
    if args.label:
        labels = {}
        for pair in args.label:
            if '=' in pair:
                items = pair.split('=')
                labels[items[0]] = items[1]
        job['labels'] = labels

    # Storage
    if args.storage:
        try:
            with open(args.storage) as json_file:
                storage = '{%s}' % json_file.read()
        except IOError as err:
            print('Error: %s' % err)
            exit(1)
        except ValueError as err:
            print('Error: %s' % err)
            exit(1)
        storage = json.loads(storage)
        if 'storage' in storage:
            job['storage'] = storage['storage']

    # Priority
    if args.priority:
        if 'policies' not in job:
            job['policies'] = {}
        job['policies']['priority'] = args.priority

    # Retries
    if args.retries:
        if 'policies' not in job:
            job['policies'] = {}
        job['policies']['maximumRetries'] = args.retries

    if args.taskretries:
        if 'policies' not in job:
            job['policies'] = {}
        job['policies']['maximumTaskRetries'] = args.taskretries

    # Maximum time in queue
    if args.maxtimeinqueue:
        if 'policies' not in job:
            job['policies'] = {}
        job['policies']['maximumTimeInQueue'] = args.maxtimeinqueue

    # Leave in queue
    if args.leaveinqueue:
        if 'policies' not in job:
            job['policies'] = {}
        job['policies']['leaveInQueue'] = args.leaveinqueue

    # Add task to job
    job['tasks'] = [task]

    # Print JSON description of job if requested
    if args.dryrun:
        print_json(job)
        exit(0)

    try:
        client = ProminenceClient(authenticated=True)
        job_id = client.create_job(job)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.JobCreationError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    print('Job created with id %d' % job_id)

    # Cleanup if necessary
    if args.directory:
        if os.path.exists('/tmp/%s.tar.gz' % tarball):
            os.unlink('/tmp/%s.tar.gz' % tarball)

def command_usage(args):
    """
    Return historical usage information
    """
    try:
        client = ProminenceClient(authenticated=True)
        usage = client.get_usage(args.start, args.end, args.group, args.all)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.UsageError) as err:
        print('Error:', err)
        exit(1)

    if 'usage' in usage:
        if 'users' in usage['usage']:
            for user in usage['usage']['users']:
                print(user)
                print('   Number of jobs             %d' % usage['usage']['users'][user]['numberOfJobs'])
                print('   CPU time (CPU hours)       %d' % usage['usage']['users'][user]['cpuTime'])
                print('   Wall time (CPU hours)      %d' % usage['usage']['users'][user]['wallTime'])
        if 'groups' in usage['usage']:
            for group in  usage['usage']['groups']:
                print(group)
                print('   Number of jobs             %d' % usage['usage']['groups'][group]['numberOfJobs'])
                print('   CPU time (CPU hours)       %d' % usage['usage']['groups'][group]['cpuTime'])
                print('   Wall time (CPU hours)      %d' % usage['usage']['groups'][group]['wallTime'])

def command_resources(args):
    """
    List resources
    """
    try:
        client = ProminenceClient(authenticated=True)
        resources = client.resources()
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError) as err:
        print('Error:', err)
        exit(1)

    print('Existing resources\n')
    print('Total           Free')
    print('Cpus  Memory    Cpus  Memory    Site')
    for line in resources['existing']:
        print('%s  %s      %s  %s      %s' % (str(line['capacity']['cpus']).ljust(4),
                                              str(line['capacity']['memory']).ljust(4),
                                              str(line['free']['cpus']).ljust(4),
                                              str(line['free']['memory']).ljust(4),
                                              str(line['site']).ljust(4)))

    print('\nPotential resources\n')
    print('--coming soon--')

def command_kv_list(args):
    """
    List keys
    """
    try:
        client = ProminenceClient(authenticated=True)
        keys = client.kv_list(args.path)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.UsageError, exceptions.KeyValueError) as err:
        print('Error:', err)
        exit(1)

    for key in keys:
        print(key)

def command_kv_delete(args):
    """
    Delete keys
    """
    try:
        client = ProminenceClient(authenticated=True)
        client.kv_delete(args.key, args.prefix)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.UsageError, exceptions.KeyValueError) as err:
        print('Error:', err)
        exit(1)

def command_kv_set(args):
    """
    Set key
    """
    value = args.value
    if os.path.isfile(args.value):
        with open(args.value) as fh:
            value = fh.read()

    try:
        client = ProminenceClient(authenticated=True)
        client.kv_set(args.key, value)
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.UsageError, exceptions.KeyValueError) as err:
        print('Error:', err)
        exit(1)

def command_kv_get(args):
    """
    Get value of a key
    """
    try:
        client = ProminenceClient(authenticated=True)
        print(client.kv_get(args.key))
    except exceptions.AuthenticationError:
        print('Error: authentication failed')
        exit(1)
    except exceptions.TokenExpiredError:
        print('Error: access token has expired')
        exit(1)
    except (exceptions.ConnectionError, exceptions.TokenError, exceptions.UsageError, exceptions.KeyValueError) as err:
        print('Error:', err)
        exit(1)
    except exceptions.NoSuchKey as err:
        print('Error: No such key')
        exit(1)

def create_parser():
    """
    Create the argument parser
    """
    parser = argparse.ArgumentParser(description='PROMINENCE - \
                                                  run jobs in containers across clouds')
    subparsers = parser.add_subparsers(help='sub-command help')

    # Create the parser for the "register" command
    parser_register = subparsers.add_parser('register',
                                            help='Register as a client with the OIDC server')
    parser_register.set_defaults(func=command_register)

    # Create the parser for the "login" command
    parser_login = subparsers.add_parser('login',
                                         help='Get a token from the OIDC server')
    parser_login.set_defaults(func=command_login)

    # Create the parser for the "run" command
    parser_run = subparsers.add_parser('run',
                                       help='Create a job or workflow from JSON in a file or URL')
    parser_run.add_argument('file',
                            help='JSON filename or URL containing JSON')
    parser_run.set_defaults(func=command_run)

    # Create the parser for the "rerun" command
    parser_rerun = subparsers.add_parser('rerun',
                                         help='Re-run all failed jobs from a completed workflow')
    parser_rerun.add_argument('id',
                              help='Workflow id',
                              type=int)
    parser_rerun.set_defaults(func=command_rerun)

    # Create the parser for the "clone" command
    parser_clone = subparsers.add_parser('clone',
                                        help='Create a new job or workflow identical to a previously-submitted one')
    parser_clone.add_argument('resource',
                             help='Resource type',
                             default='job',
                             nargs='?',
                             choices=['job', 'workflow'])
    parser_clone.add_argument('id',
                             help='Job or workflow id',
                             type=int)
    parser_clone.set_defaults(func=command_clone)

    # Create the parser for the "create" command
    parser_create = subparsers.add_parser('create',
                                          help='Create a job')
    parser_create.add_argument('--name',
                               dest='name',
                               default='',
                               help='Job name.')
    parser_create.add_argument('--memory',
                               dest='memory',
                               default=1,
                               type=int,
                               help='Memory in GB per node. Only one of --memory or --memory-per-cpu can be specified.')
    parser_create.add_argument('--memory-per-cpu',
                               dest='memorypercpu',
                               default=0,
                               type=int,
                               help='Memory in GB per core per node. Only one of --memory or --memory-per-cpu can be \
                                     specified.')
    parser_create.add_argument('--cpus',
                               dest='cpus',
                               default=1,
                               type=int,
                               help='Cores per node. Only one of --cpus, --cpus-range or --cpus-options can be specified.')
    parser_create.add_argument('--cpus-range',
                               dest='cpusrange',
                               default='',
                               type=str,
                               help='Range of cores per node, e.g. "16,32" will result in anywhere between 16 and 32 \
                                     cores being used, with larger values preferred. Only one of --cpus, --cpus-range or \
                                     --cpus-options can be specified.')
    parser_create.add_argument('--cpus-options',
                               dest='cpusoptions',
                               default='',
                               type=str,
                               help='Optional numbers of cores per node, e.g. "14,28" will result in either 28 or 14 \
                                     cores being used, with 28 preferred. Only one of --cpus, --cpus-range or \
                                     --cpus-options can be specified.')
    parser_create.add_argument('--nodes',
                               dest='nodes',
                               default=1,
                               type=int,
                               help='Number of nodes. Only one of --nodes or --total-cpus-range can be specified.')
    parser_create.add_argument('--total-cpus-range',
                               dest='totalcpusrange',
                               default='',
                               help='Range of total number of CPUs for multi-node jobs, e.g. "64,128" will result in \
                                     anywhere between 64 and 128 cores being used, with the specified range of CPUs being \
                                     respected, and the number of nodes as required. Only one of --nodes or --total-cpus-range \
                                     can be specified.')
    parser_create.add_argument('--procs-per-node',
                               dest='ppn',
                               default=0,
                               type=int,
                               help='Number of MPI processes to launch per node. By default this \
                                     will be the number of CPU cores available per node but it can \
                                     be changed if necessary.')
    parser_create.add_argument('--omp-procs-per-node',
                               dest='ompppn',
                               default=0,
                               type=int,
                               help='Number of OpenMP threads to launch per node. The number of MPI \
                                     processes per node will be reduced accordingly.')
    parser_create.add_argument('--disk',
                               dest='disk',
                               default=10,
                               type=int,
                               help='Size of disk containing the job\'s scratch directory. For \
                                     multi-node jobs it will be shared across each of the nodes. \
                                     By default a 10 GB disk will be used.')
    parser_create.add_argument('--walltime',
                               dest='walltime',
                               type=int,
                               help='Walltime limit in minutes. If the job is still running after \
                                     this time it will be killed.')
    parser_create.add_argument('--openmpi',
                               dest='openmpi',
                               default=False,
                               action='store_true',
                               help="Specify that this is an OpenMPI job.")
    parser_create.add_argument('--mpich',
                               dest='mpich',
                               default=False,
                               action='store_true',
                               help="Specify that this is an MPICH job.")
    parser_create.add_argument('--intelmpi',
                               dest='intelmpi',
                               default=False,
                               action='store_true',
                               help="Specify that this is an Intel MPI job.")
    parser_create.add_argument('--artifact',
                               dest='artifact',
                               action='append',
                               help='A URL to be transferred to the job. Archives will be \
                                     automatically unpacked/extracted. Optionally, for the \
                                     case of a tarball or zip archive, a directory name and \
                                     mount point can be specified by using the format \
                                     "<URL>:<directory>:<mountpoint>". The mount point must be \
                                     an absolute path. \
                                     This option can be specified multiple times.')
    parser_create.add_argument('--input',
                               dest='inputfile',
                               action='append',
                               help='Full path to a file on the current host to be \
                                     uploaded and made available to the job. This option \
                                     can be specified multiple times to set multiple output files.')
    parser_create.add_argument('--output',
                               dest="outputfile",
                               action='append',
                               help='An output file to be copied to transient storage. This option \
                                     can be specified multiple times to set multiple output files.')
    parser_create.add_argument('--outputdir',
                               dest="outputdir",
                               action='append',
                               help='A directory to be copied to transient storage. This option \
                                     can be specified multiple times to set multiple directories.')
    parser_create.add_argument('--workdir',
                               dest='workdir',
                               help='Set the current working directory.')
    parser_create.add_argument('--env',
                               dest='env',
                               action='append',
                               help='Specify environment variables in the form name=value. \
                                     This option can be specified multiple times to set \
                                     multiple environment variables.')
    parser_create.add_argument('--label',
                               dest='label',
                               action='append',
                               help='Set metadata in the form key=value. This option can \
                                     be specified multiple times to set multiple labels.')
    parser_create.add_argument('--runtime',
                               dest='runtime',
                               choices=['singularity', 'udocker'],
                               help='Container runtime, either singularity or udocker. The default \
                                     is singularity.')
    parser_create.add_argument('--retries',
                               dest='retries',
                               type=int,
                               help='Number of job retries if the application exit code is not 0. By \
                                     default no retries will be attempted.')
    parser_create.add_argument('--task-retries',
                               dest='taskretries',
                               type=int,
                               help='Number of task retries if the application exit code is not 0. By \
                                     default no retries will be attempted.')
    parser_create.add_argument('--max-time-in-queue',
                               dest='maxtimeinqueue',
                               type=int,
                               help='By default jobs will fail quickly if deployment is not possible. By \
                                     setting the maximum time in queue to a non-zero value enables jobs \
                                     to wait in the queue until resources become available. Units are \
                                     minutes.')
    parser_create.add_argument('--leave-in-queue',
                               dest='leaveinqueue',
                               default=False,
                               action='store_true',
                               help='Leave job in queue after successful completion, failure, deletion or being killed. \
                                     This avoids the need for using "--completed" to see the job.')
    parser_create.add_argument('--priority',
                               dest='priority',
                               type=int,
                               help='Set job priority, allowing users to influence the order in which their jobs \
                                     are run. Higher priority jobs are run first, resources permitting.')
    parser_create.add_argument('--directory',
                               dest='directory',
                               help='Path to a directory to be transferred to the job. The job \
                                     will be executed within this directory.')
    parser_create.add_argument('--storage',
                               dest='storage',
                               help='Filename specifying storage details')
    parser_create.add_argument('--dry-run',
                               dest='dryrun',
                               default=False,
                               action='store_true',
                               help='Print json to stdout but do not actually create job.')
    parser_create.add_argument('image',
                               help='Container image')
    parser_create.add_argument('command',
                               nargs='?',
                               help='Command to run in the container. If you need to specify \
                                     arguments, put the combined command and arguments inside quotes.')
    parser_create.set_defaults(func=command_create)

    # Create the parser for the "list" command
    parser_list = subparsers.add_parser('list',
                                        help='List jobs or workflows')
    parser_list.add_argument('--completed',
                             dest='completed',
                             default=False,
                             help='List completed jobs/workflows',
                             action='store_true')
    parser_list.add_argument('-r',
                             '--running',
                             dest='running',
                             default=False,
                             action='store_true',
                             help='List only running jobs/workflows')
    parser_list.add_argument('-i',
                             '--idle',
                             dest='idle',
                             default=False,
                             action='store_true',
                             help='List only idle jobs/workflows')
    parser_list.add_argument('-n',
                             '--last',
                             dest='num',
                             default=1,
                             type=int,
                             help='Number of completed jobs/workflows to return')
    parser_list.add_argument('--constraint',
                             dest='constraint',
                             action='append',
                             help='Constraint of the form key=value. This option can be specified \
                                   multiple times if multiple constraints are needed.')
    parser_list.add_argument('--name',
                             dest='name',
                             help='Constraint on the job/workflow name')
    parser_list.add_argument('-a',
                             '--all',
                             dest='all',
                             default=False,
                             action='store_true',
                             help='List jobs/workflows in all states')
    parser_list.add_argument('resource',
                             help='Resource type',
                             default='jobs',
                             nargs='?',
                             choices=['jobs', 'workflows'])
    parser_list.add_argument('id',
                             help='Workflow id',
                             nargs='?',
                             type=int)
    parser_list.set_defaults(func=command_list)

    # Create the parser for the "describe" command
    parser_describe = subparsers.add_parser('describe',
                                            help='Describe a job or workflow')
    parser_describe.add_argument('resource',
                                 help='Resource type',
                                 default='job',
                                 nargs='?',
                                 choices=['job', 'workflow'])
    parser_describe.add_argument('id',
                                 help='Job id',
                                 type=int)
    parser_describe.set_defaults(func=command_describe)

    # Create the parser for the "delete" command
    parser_delete = subparsers.add_parser('delete',
                                          help='Delete a job or workflow')
    parser_delete.add_argument('resource',
                               help='Resource type',
                               default='job',
                               nargs='?',
                               choices=['job', 'workflow'])
    parser_delete.add_argument('id',
                               help='Job/workflow id',
                               type=int)
    parser_delete.set_defaults(func=command_delete)

    # Create the parser for the "remove" command
    parser_remove = subparsers.add_parser('remove',
                                          help='Remove a job or workflow from the queue')
    parser_remove.add_argument('resource',
                               help='Resource type',
                               default='job',
                               nargs='?',
                               choices=['job', 'workflow'])
    parser_remove.add_argument('id',
                               help='Job/workflow id',
                               type=int)
    parser_remove.set_defaults(func=command_remove)

    # Create the parser for the "stdout" command
    parser_stdout = subparsers.add_parser('stdout',
                                          help='Get standard output from a running or completed job')
    parser_stdout.add_argument('id',
                               help='Job or workflow id',
                               type=int)
    parser_stdout.add_argument('job',
                               help='Job name',
                               nargs='?')
    parser_stdout.add_argument('instance',
                               help='Instance',
                               nargs='?',
                               default=-1,
                               type=int)
    parser_stdout.add_argument('-n',
                               '--node',
                               dest='node',
                               default=0,
                               type=int,
                               help='Display stdout from this node for the case of multi-node jobs')
    parser_stdout.set_defaults(func=command_stdout)

    # Create the parser for the "stderr" command
    parser_stderr = subparsers.add_parser('stderr',
                                          help='Get standard error from a running or completed job')
    parser_stderr.add_argument('id',
                               help='Job or workflow id',
                               type=int)
    parser_stderr.add_argument('job',
                               help='Job name',
                               nargs='?')
    parser_stderr.add_argument('instance',
                               help='Instance',
                               nargs='?',
                               default=-1,
                               type=int)
    parser_stderr.add_argument('-n',
                               '--node',
                               dest='node',
                               default=0,
                               type=int,
                               help='Display stderr from this node for the case of multi-node jobs')
    parser_stderr.set_defaults(func=command_stderr)

    # Create the parser for the "exec" command
    parser_exec = subparsers.add_parser('exec',
                                        help='Execute a command inside a job')
    parser_exec.add_argument('id',
                                 help='Job id',
                                 type=int)
    parser_exec.add_argument('command',
                             nargs='?',
                             help='Command to run in the container. If you need to specify \
                                   arguments, put the combined command and arguments inside quotes.')
    parser_exec.set_defaults(func=command_exec)

    # Create the parser for the "snapshot" command
    parser_snapshot = subparsers.add_parser('snapshot',
                                            help='Create and download a snapshot of a file or directory in a running job')
    parser_snapshot.add_argument('id',
                                 help='Job id',
                                 type=int)
    parser_snapshot.add_argument('path',
                                 help='Path of file or directory to snapshot')
    parser_snapshot.set_defaults(func=command_snapshot)

    # Create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload',
                                          help='Upload a file to transient storage')
    parser_upload.add_argument('--name',
                               dest='name',
                               help='Name to be used by jobs to identity the file')
    parser_upload.add_argument('--filename',
                               dest='filename',
                               help='Local filename')
    parser_upload.add_argument('--checksum',
                               dest='checksum',
                               default=None,
                               help='SHA256 checksum')
    parser_upload.set_defaults(func=command_upload)

    # Create the parser for the "download" command
    parser_download = subparsers.add_parser('download',
                                            help='Download output files from a completed job or workflow')
    parser_download.add_argument('--force',
                                 dest='force',
                                 default=False,
                                 help='Force overwrite of existing file',
                                 action='store_true')
    parser_download.add_argument('--dir',
                                 dest='dir',
                                 default=False,
                                 help='Save output files in a directory named by the job id',
                                 action='store_true')
    parser_download.add_argument('resource',
                                 help='Resource type',
                                 default='job',
                                 nargs='?',
                                 choices=['job', 'workflow'])
    parser_download.add_argument('id',
                                 help='Job/workflow id',
                                 type=int)
    parser_download.set_defaults(func=command_download)

    # Create the parser for the "ls" command
    parser_ls = subparsers.add_parser('ls',
                                      help='List output files')
    parser_ls.add_argument('-l',
                           '--long',
                           dest='long',
                           default=False,
                           action='store_true',
                           help='Show object sizes and last modification times.')

    parser_ls.add_argument('path',
                           nargs='?',
                           help='Path')
    parser_ls.set_defaults(func=command_ls)

    # Create the parser for the "rm" command
    parser_rm = subparsers.add_parser('rm',
                                      help='Delete a file uploaded to object storage')
    parser_rm.add_argument('object',
                           help='Object name')
    parser_rm.set_defaults(func=command_rm)

    # Create the parser for the "resources" command
    parser_resources = subparsers.add_parser('resources',
                                             help='List available resources')
    parser_resources.set_defaults(func=command_resources)

    # Create the parser for the "usage" command
    parser_usage = subparsers.add_parser('usage',
                                          help='Return historical usage information')
    parser_usage.add_argument('--group',
                                 dest='group',
                                 default=False,
                                 help='Return usage by group',
                                 action='store_true')
    parser_usage.add_argument('--all',
                                 dest='all',
                                 default=False,
                                 help='Show all users in the group',
                                 action='store_true')
    parser_usage.add_argument('start',
                              help='Start date in the form YYYY-MM-DD')
    parser_usage.add_argument('end',
                              help='End date in the form YYYY-MM-DD')
    parser_usage.set_defaults(func=command_usage)

    # Create the parser for the "kv" command
    parser_kv = subparsers.add_parser('kv',
                                      help='Interact with the key-value store')
    kv_subparsers = parser_kv.add_subparsers()

    #  Create the parser for the "kv list" command
    parser_kv_list = kv_subparsers.add_parser('list',
                                        help='List keys')
    parser_kv_list.add_argument('path',
                                help='Path',
                                nargs='?')
    parser_kv_list.set_defaults(func=command_kv_list)

    #  Create the parser for the "kv delete" command
    parser_kv_delete = kv_subparsers.add_parser('delete',
                                        help='Delete key')
    parser_kv_delete.add_argument('--prefix',
                           dest='prefix',
                           default=False,
                           help='Delete a range of keys beginning with the specified prefix',
                           action='store_true')
    parser_kv_delete.add_argument('key',
                                  help='Key')
    parser_kv_delete.set_defaults(func=command_kv_delete)

    #  Create the parser for the "kv set" command
    parser_kv_set = kv_subparsers.add_parser('set',
                                        help='Set key-value pair; a value or filename must be specified')
    parser_kv_set.add_argument('key',
                               help='Key')
    parser_kv_set.add_argument('value',
                               help='Value or filename')
    parser_kv_set.set_defaults(func=command_kv_set)

    #  Create the parser for the "kv get" command
    parser_kv_get = kv_subparsers.add_parser('get',
                                        help='Get value of specified key')
    parser_kv_get.add_argument('key',
                               help='Key')
    parser_kv_get.set_defaults(func=command_kv_get)

    # Version
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(__version__),
                        help='show the version number and exit')

    return parser

def main(argv=None):
    # Check that the URL for the PROMINENCE service exists; if not, define a default
    if 'PROMINENCE_URL' not in os.environ:
        os.environ['PROMINENCE_URL'] = 'https://host-130-246-215-158.nubes.stfc.ac.uk/prominence/v1'

    # Parse the arguments
    parser = create_parser()
    args = parser.parse_args(argv)

    # Run the required function
    try:
        a = getattr(args, "func")
    except AttributeError:
        parser.print_help()
    else:
        args.func(args)
