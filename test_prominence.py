from prominence.cli import main
import json
import pytest

default_resources = {"nodes": 1, "disk": 10, "cpus": 1, "memory": 1}
default_tasks = [{"image": "centos:7", "runtime": "singularity"}]

def test_create(capsys):
    """
    Test basic job create
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks}

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
    assert data == {"resources": default_resources, "name": "", "tasks": [{"image": "centos:7", "runtime": "udocker"}]}

def test_create_fixed_cpus(capsys):
    """
    Test job create with fixed cpus
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--cpus=16", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpus": 16, "memory": 1}, "name": "", "tasks": default_tasks}

def test_create_fixed_memory(capsys):
    """
    Test job create with fixed memory
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--memory=16", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpus": 1, "memory": 16}, "name": "", "tasks": default_tasks}

def test_create_fixed_disk(capsys):
    """
    Test job create with fixed disk
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--disk=20", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 20, "cpus": 1, "memory": 1}, "name": "", "tasks": default_tasks}

def test_create_walltime(capsys):
    """
    Test job create with walltime
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--walltime=12345", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpus": 1, "memory": 1, "walltime": 12345}, "name": "", "tasks": default_tasks}

def test_create_cpus_range(capsys):
    """
    Test job create with cpus range
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--cpus-range=16,32", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpusRange": [16, 32], "memory": 1}, "name": "", "tasks": default_tasks}

def test_create_total_cpus_range_and_cpus_range(capsys):
    """
    Test job create with total cpus range and cpus range
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--total-cpus-range=16,32", "--cpus-range=4,8", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"disk": 10, "totalCpusRange": [16, 32], "cpusRange": [4, 8], "memory": 1}, "name": "", "tasks": default_tasks}

def test_create_cpus_options(capsys):
    """
    Test job create with cpus options
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--cpus-options=16,32", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpusOptions": [16, 32], "memory": 1}, "name": "", "tasks": default_tasks}

def test_create_memory_per_cpu(capsys):
    """
    Test job create with memory per cpu
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--memory-per-cpu=16", "--cpus=2", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 1, "disk": 10, "cpus": 2, "memoryPerCpu": 16}, "name": "", "tasks": default_tasks}

def test_create_nodes_openmpi(capsys):
    """
    Test job create with fixed nodes with OpenMPI
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--nodes=2", "--openmpi", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 1, "memory": 1}, "name": "", "tasks": [{"image": "centos:7", "runtime": "singularity", "type": "openmpi"}]}

def test_create_nodes_intelmpi(capsys):
    """
    Test job create with fixed nodes with Intel MPI
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--nodes=2", "--intelmpi", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 1, "memory": 1}, "name": "", "tasks": [{"image": "centos:7", "runtime": "singularity", "type": "intelmpi"}]}

def test_create_nodes_mpich(capsys):
    """
    Test job create with fixed nodes with MPICH
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--nodes=2", "--mpich", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 1, "memory": 1}, "name": "", "tasks": [{"image": "centos:7", "runtime": "singularity", "type": "mpich"}]}

def test_create_leave_in_queue(capsys):
    """
    Test job create with leave in queue
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--leave-in-queue", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "policies": {"leaveInQueue": True}}

def test_create_priority(capsys):
    """
    Test job create with priority
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--priority=8", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "policies": {"priority": 8}}

def test_create_max_time_in_queue(capsys):
    """
    Test job create with max time in queue
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--max-time-in-queue=864000", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "policies": {"maximumTimeInQueue": 864000}}

def test_create_retries(capsys):
    """
    Test job create with retries
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--retries=4", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "policies": {"maximumRetries": 4}}

def test_create_workdir(capsys):
    """
    Test job create with workdir
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--workdir=/data", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": [{"image": "centos:7", "runtime": "singularity", "workdir": "/data"}]}

def test_create_labels(capsys):
    """
    Test job create with labels
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--label=app=app1", "--label=version=1.2.3", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "labels": {"app": "app1", "version": "1.2.3"}}

def test_create_env(capsys):
    """
    Test job create with env variables
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--env=var1=2", "--env=var2=a2", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": [{"image": "centos:7", "runtime": "singularity", "env": {"var1":"2", "var2":"a2"}}]}

def test_create_procs_per_node(capsys):
    """
    Test job create with procs per node
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--nodes=2", "--cpus=2", "--openmpi", "--procs-per-node=1", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": {"nodes": 2, "disk": 10, "cpus": 2, "memory": 1}, "name": "", "tasks": [{"image": "centos:7", "runtime": "singularity", "type": "openmpi", "procsPerNode": 1}]}

def test_create_artifacts(capsys):
    """
    Test job create with artifacts
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--artifact=testartifact1", "--artifact=testartifact2", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "artifacts": [{"url": "testartifact1"}, {"url": "testartifact2"}]}

def test_create_artifact_mount(capsys):
    """
    Test job create with artifact mount
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--artifact=testartifact.tgz:testdir:/data", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "artifacts": [{"url": "testartifact.tgz", "mountpoint": "testdir:/data"}]}

def test_create_input_file(capsys):
    """
    Test job create with input file
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--input=test.txt", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "inputs": [{"filename": "test.txt", "content": "aGVsbG8K"}]}

def test_create_output_files(capsys):
    """
    Test job create with output files
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--output=out1.cdf", "--output=out2.cdf", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "outputFiles": ["out1.cdf", "out2.cdf"]}

def test_create_output_directories(capsys):
    """
    Test job create with output directories
    """
    with pytest.raises(SystemExit):
        main(["create", "--dry-run", "--outputdir=out1", "--outputdir=out2", "centos:7"])
    data = json.loads(capsys.readouterr().out)
    assert data == {"resources": default_resources, "name": "", "tasks": default_tasks, "outputDirs": ["out1", "out2"]}
