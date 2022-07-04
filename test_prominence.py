"""Test PROMINENCE CLI"""
import json
import pytest
from prominence.cli import main
from prominence import Resources, JobPolicies, Notification, Task, Job

default_resources = {"nodes": 1, "disk": 10, "cpus": 1, "memory": 1}
default_tasks = [{"image": "centos:7", "runtime": "singularity"}]
default_tasks_1 = [{'image': 'centos:7', 'runtime': 'singularity', 'cmd': 'hostname'}]

def test_create(capsys):
    """
    Test basic job create
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks}

def test_create_command(capsys):
    """
    Test job with command
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "centos:7", "hostname"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": [{"image": "centos:7", "runtime": "singularity", "cmd": "hostname"}]}

def test_create_name(capsys):
    """
    Test job create with name
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--name=hello", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "hello", "tasks": default_tasks}

def test_create_udocker(capsys):
    """
    Test job create with udocker
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--runtime=udocker", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": [{"image": "centos:7", "runtime": "udocker"}]}

def test_create_fixed_cpus(capsys):
    """
    Test job create with fixed cpus
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--cpus=16", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpus": 16, "memory": 1},
                    "name": "",
                    "tasks": default_tasks}

def test_create_fixed_memory(capsys):
    """
    Test job create with fixed memory
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--memory=16", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpus": 1, "memory": 16},
                    "name": "",
                    "tasks": default_tasks}

def test_create_fixed_disk(capsys):
    """
    Test job create with fixed disk
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--disk=20", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 20, "cpus": 1, "memory": 1},
                    "name": "",
                    "tasks": default_tasks}

def test_create_walltime(capsys):
    """
    Test job create with walltime
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--walltime=12345", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1,
                                  "disk": 10,
                                  "cpus": 1,
                                  "memory": 1,
                                  "walltime": 12345},
                    "name": "",
                    "tasks": default_tasks}

def test_create_cpus_range(capsys):
    """
    Test job create with cpus range
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--cpus-range=16,32", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpusRange": [16, 32], "memory": 1},
                    "name": "",
                    "tasks": default_tasks}

def test_create_total_cpus_range_and_cpus_range(capsys):
    """
    Test job create with total cpus range and cpus range
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--total-cpus-range=16,32", "--cpus-range=4,8", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"disk": 10,
                                  "totalCpusRange": [16, 32],
                                  "cpusRange": [4, 8],
                                  "memory": 1},
                    "name": "",
                    "tasks": default_tasks}

def test_create_cpus_options(capsys):
    """
    Test job create with cpus options
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--cpus-options=16,32", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpusOptions": [16, 32], "memory": 1},
                    "name": "",
                    "tasks": default_tasks}

def test_create_memory_per_cpu(capsys):
    """
    Test job create with memory per cpu
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--memory-per-cpu=16", "--cpus=2", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpus": 2, "memoryPerCpu": 16},
                    "name": "",
                    "tasks": default_tasks}

def test_create_nodes_openmpi(capsys):
    """
    Test job create with fixed nodes with OpenMPI
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--nodes=2", "--openmpi", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 1, "memory": 1},
                    "name": "",
                    "tasks": [{"image": "centos:7", "runtime": "singularity", "type": "openmpi"}]}

def test_create_nodes_intelmpi(capsys):
    """
    Test job create with fixed nodes with Intel MPI
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--nodes=2", "--intelmpi", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 1, "memory": 1},
                    "name": "",
                    "tasks": [{"image": "centos:7", "runtime": "singularity", "type": "intelmpi"}]}

def test_create_nodes_mpich(capsys):
    """
    Test job create with fixed nodes with MPICH
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--nodes=2", "--mpich", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 1, "memory": 1},
                    "name": "",
                    "tasks": [{"image": "centos:7", "runtime": "singularity", "type": "mpich"}]}

def test_create_leave_in_queue(capsys):
    """
    Test job create with leave in queue
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--leave-in-queue", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "policies": {"leaveInQueue": True}}

def test_create_priority(capsys):
    """
    Test job create with priority
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--priority=8", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "policies": {"priority": 8}}

def test_create_max_time_in_queue(capsys):
    """
    Test job create with max time in queue
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--max-time-in-queue=864000", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "policies": {"maximumTimeInQueue": 864000}}

def test_create_job_retries(capsys):
    """
    Test job create with job retries
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--retries=4", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "policies": {"maximumRetries": 4}}

def test_create_task_retries(capsys):
    """
    Test job create with task retries
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--task-retries=4", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "policies": {"maximumTaskRetries": 4}}

def test_create_workdir(capsys):
    """
    Test job create with workdir
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--workdir=/data", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": [{"image": "centos:7", "runtime": "singularity", "workdir": "/data"}]}

def test_create_labels(capsys):
    """
    Test job create with labels
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--label=app=app1", "--label=version=1.2.3", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "labels": {"app": "app1", "version": "1.2.3"}}

def test_create_env(capsys):
    """
    Test job create with env variables
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--env=var1=2", "--env=var2=a2", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": [{"image": "centos:7",
                               "runtime": "singularity",
                               "env": {"var1":"2", "var2":"a2"}}]}

def test_create_procs_per_node(capsys):
    """
    Test job create with procs per node
    """
    with pytest.raises(SystemExit):
        main(["create",
              "--dry-run",
              "--nodes=2",
              "--cpus=2",
              "--openmpi",
              "--procs-per-node=1",
              "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 2, "memory": 1},
                    "name": "",
                    "tasks": [{"image": "centos:7",
                               "runtime": "singularity",
                               "type": "openmpi",
                               "procsPerNode": 1}]}

def test_create_artifacts(capsys):
    """
    Test job create with artifacts
    """
    with pytest.raises(SystemExit):
        main(["create",
              "--dry-run",
              "--artifact=testartifact1",
              "--artifact=testartifact2",
              "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "artifacts": [{"url": "testartifact1"}, {"url": "testartifact2"}]}

def test_create_artifact_mount(capsys):
    """
    Test job create with artifact mount
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--artifact=testartifact.tgz:testdir:/data", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "artifacts": [{"url": "testartifact.tgz", "mountpoint": "testdir:/data"}]}

def test_create_input_file(capsys):
    """
    Test job create with input file
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--input=test.txt", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "inputs": [{"filename": "test.txt", "content": "aGVsbG8K"}]}

def test_create_output_files(capsys):
    """
    Test job create with output files
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--output=out1.cdf", "--output=out2.cdf", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks, "outputFiles": ["out1.cdf", "out2.cdf"]}

def test_create_output_directories(capsys):
    """
    Test job create with output directories
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--outputdir=out1", "--outputdir=out2", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources,
                    "name": "",
                    "tasks": default_tasks,
                    "outputDirs": ["out1", "out2"]}

def test_python_resources_basic():
    """
    Default resources
    """
    resources = Resources()
    assert resources.json() == {"cpus": 1, "memory": 1, "disk": 10, "nodes": 1}

def test_python_resources_cpus():
    """
    Default resources with cpus modified
    """
    resources = Resources(cpus=8)
    assert resources.json() == {"cpus": 8, "memory": 1, "disk": 10, "nodes": 1}

def test_python_resources_memory():
    """
    Default resources with memory modified
    """
    resources = Resources(memory=16)
    assert resources.json() == {"cpus": 1, "memory": 16, "disk": 10, "nodes": 1}

def test_python_resources_disk():
    """
    Default resources with disk modified
    """
    resources = Resources(disk=20)
    assert resources.json() == {"cpus": 1, "memory": 1, "disk": 20, "nodes": 1}

def test_python_resources_nodes():
    """
    Default resources with nodes modified
    """
    resources = Resources(nodes=4)
    assert resources.json() == {"cpus": 1, "memory": 1, "disk": 10, "nodes": 4}

def test_python_resources_walltime():
    """
    Default resources with walltime modified
    """
    resources = Resources(walltime=5678)
    assert resources.json() == {"cpus": 1, "memory": 1, "disk": 10, "nodes": 1, "walltime": 5678}

def test_python_resources_memory_per_cpu():
    """
    Default resources with memory per cpu set
    """
    resources = Resources()
    resources.memory_per_cpu = 8
    assert resources.json() == {"cpus": 1, "disk": 10, "nodes": 1, "memoryPerCpu": 8}

def test_python_resources_cpus_range():
    """
    Default resources with cpus range set
    """
    resources = Resources()
    resources.cpus_range.min = 4
    resources.cpus_range.max = 16
    assert resources.json() == {"cpus": 1, "memory": 1, "disk": 10, "nodes": 1, "cpusRange": [4, 16]}

def test_python_resources_cpus_options():
    """
    Default resources with cpus options set
    """
    resources = Resources()
    resources.cpus_options.min = 4
    resources.cpus_options.max = 16
    assert resources.json() == {"cpus": 1, "memory": 1, "disk": 10, "nodes": 1, "cpusOptions": [4, 16]}

def test_python_resources_total_cpus_range():
    """
    Default resources with total cpus range set
    """
    resources = Resources()
    resources.total_cpus_range.min = 4
    resources.total_cpus_range.max = 16
    assert resources.json() == {"cpus": 1, "memory": 1, "disk": 10, "nodes": 1, "totalCpusRange": [4, 16]}

def test_python_task_basic():
    """
    Basic task
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'
    assert task.json() == {'image': 'centos:7', 'runtime': 'singularity', 'cmd': 'hostname'}

def test_python_task_basic_no_command():
    """
    Basic task with no command
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    assert task.json() == {'image': 'centos:7', 'runtime': 'singularity'}

def test_python_task_udocker():
    """
    Basic task using udocker
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'udocker'
    task.command = 'hostname'
    assert task.json() == {'image': 'centos:7', 'runtime': 'udocker', 'cmd': 'hostname'}

def test_python_task_workdir():
    """
    Task with work directory
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'
    task.workdir = '/data'
    assert task.json() == {'image': 'centos:7', 'runtime': 'singularity', 'cmd': 'hostname', 'workdir': '/data'}

def test_python_task_env():
    """
    Task with environment variables
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'
    task.env = {'env1': 'value1', 'env2': 'value2'}
    assert task.json() == {'image': 'centos:7', 'runtime': 'singularity', 'cmd': 'hostname', 'env': {'env1': 'value1', 'env2': 'value2'}}

def test_python_task_procs_per_node():
    """
    Task with procs per node set
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'
    task.procs_per_node = 8
    assert task.json() == {'image': 'centos:7', 'runtime': 'singularity', 'cmd': 'hostname', 'procsPerNode': 8}

def test_python_job_basic():
    """
    Basic job
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'

    job = Job()
    job.tasks.append(task)
    assert job.json() == {'tasks': default_tasks_1,
                          'name': '',
                          'resources': default_resources}

def test_python_job_name():
    """
    Job name
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'

    job = Job()
    job.name = 'test1'
    job.tasks.append(task)
    assert job.json() == {'tasks': default_tasks_1,
                          'name': 'test1',
                          'resources': default_resources}

def test_python_job_labels():
    """
    Job labels
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'

    job = Job()
    job.labels = {'app': 'tensorflow'}
    job.tasks.append(task)
    assert job.json() == {'tasks': default_tasks_1,
                          'name': '',
                          'resources': default_resources,
                          'labels': {'app': 'tensorflow'}}


def test_python_job_resources():
    """
    Job with resources defined
    """
    task = Task()
    task.image = 'centos:7'
    task.runtime = 'singularity'
    task.command = 'hostname'

    resources = Resources()
    resources.cpus = 2
    resources.memory = 4
    resources.disk = 8
    resources.walltime = 6000

    job = Job()
    job.resources = resources
    job.tasks.append(task)
    assert job.json() == {'tasks': default_tasks_1,
                          'name': '',
                          'resources': {'cpus': 2, 'memory': 4, 'disk': 8, 'walltime': 6000, 'nodes': 1}}

def test_python_job_two_tasks():
    """
    Job with two tasks
    """
    task1 = Task()
    task1.image = 'centos:7'
    task1.runtime = 'singularity'
    task1.command = 'hostname'

    task2 = Task()
    task2.image = 'centos:8'
    task2.runtime = 'singularity'
    task2.command = 'pwd'

    job = Job()
    job.tasks.append(task1)
    job.tasks.append(task2)
    assert job.json() == {'tasks': [{'image': 'centos:7', 'runtime': 'singularity', 'cmd': 'hostname'},
                                    {'image': 'centos:8', 'runtime': 'singularity', 'cmd': 'pwd'}],
                          'name': '',
                          'resources': default_resources}
