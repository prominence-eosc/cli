# Change Log

## 0.21.0
* Support floating point memory and memory per CPU.

## 0.20.2
* (bug fix) `--concurrency` option when downloading now works correctly.

## 0.20.1
* (bug fix) Adding `--input` broke some things due to a minor bug.

## 0.20.0
* Added a `--input` option to the `describe` command. This returns only the original JSON which can easily be used for cloning.
* Added automatic selection of container runtime to the Python client, using the same method as used in the CLI.

## 0.19.0
* Support tailing standard output/error using `--tail` option to `stdout` and `stderr`.
* (bug fix) Information about job factories now included in `prominence describe workflow`.
* If a file specified as `file://...` in `inputs` doesn't exist, report a meaningful error.

## 0.18.3
* Job status wasn't being updated correctly in the Python API, now fixed.

## 0.18.2
* Support download of output files & directories for jobs in the `killed` state.

## 0.18.1
* Support uploads of files > 2 GB in size by disabling checksums (Python requests/urllib3 don't support streaming uploads of large files when additional data needs to be specified).

## 0.18.0
* Download of output files/directories from jobs in a workflow is parallelised.
* Increased default timeout for interacting with the REST API from 30s to 150s.
* Added improved Python API making it easier to write workflows as code.

## 0.17.0
* Support for user-supplied SHA256 checksums and calculation of checksums for S3 storage.
* Initial support for uploads to Azure blob storage.
* Added `resources` command to list available resources.

## 0.16.0
* Added a `--node` option to the `stdout` and `stderr` commands so that standard output/error can be viewed from a specified
node (0, 1, 2, ...) for the case of multi-node jobs. By default standard output/error from the first node (0) is displayed.
* The time taken to stage-in all files (`stageInTime`) and the time taken to stage-out all output data (`stageOutTime`) is
displayed when the `--describe` command is run for completed jobs.
* Support `--memory-per-cpu`, `--cpus-range`, `--cpus-options` and `--cpus-total-range` in `prominence create`.
* Added `--directory` option to `prominence create` which automatically transfers contents of specified directory to the job.
* Include `provisionedResources`, `imageSha256` and `runtimeVersion` in the output of `prominence describe`.
* Added `clone` command to create a clone of a previous job or workflow.
* Added `remove` command to remove a completed job or workflow from the queue.
* Added `--priority` option to `prominence create` for specifying job priority.
* Added commands for interacting with the key-value store.
* Added `--task-retries`, now separate to job retries.

## 0.15.0
* When downloading output files/directories from jobs which were generated by a job factory, if the output file/directory name
contains a parameter it will be replaced as appropriate.

## 0.14.0
* The `download` command can be used to download output files/directories from all jobs associated with a workflow.

## 0.13.1
* (bug fix) Handle situation with no `cmd` defined in code introduced in 0.13.0

## 0.13.0
* If a `cmd` contains multiple lines, the task will be split automatically into multiple tasks with one `cmd` per task. However, if the
first line begins with a shebang, an input file will be created automatically and the task will execute this input file. This functionality
is particularly helpful for job descriptions in the YAML format.
* (bug fix) If snapshot download fails report name of requested file/directory properly

## 0.12.1
* (bug fix) Handle correctly JSON descriptions with already expanded input files

## 0.12.0
* If input files in job descriptions are in the form of a list of names beginning with `file://`, the specified files will be read and
the content automatically added to the job description. This results in much simpler and clearer job description files.

## 0.11.0
* Accept job and workflow descriptions in YAML format. These are converted to JSON before being POSTed to the REST API. YAML format makes it simpler to specify commands without having to worry about escaping characters.

## 0.10.0
* Accept token from `PROMINENCE_TOKEN` environment variable

## 0.9.0
* Include CPU info when describing complete jobs

## 0.8.1
* No longer use deprecated `verify` parameter in `jwt.decode`

## 0.8.0
* Addded default URLs of the PROMINENCE and OIDC servers to make things easier for some users
* Removed ability to mark a job as being preemptible, as this functionality has not yet been implemented anyway

## 0.7.0
* Added an option `--name` to the `list` command which enables users to list only jobs or workflows which a specific name

## 0.6.0
* Added an option `--all` to the `usage` command which shows usage by user in the user's group
* Added an option `--maxtimeinqueue` when creating jobs to enable users to specify the maximum time that a job should remain in the queue while waiting for resources

## 0.5.0
* The udocker runtime is automatically selected if the container image is a URL for a file with extension `.tgz`
* Added `rerun` command to re-run any failed jobs from a completed workflow

## 0.4.0
 * Added `usage` command to obtain historical CPU usage data

## 0.3.0
* Added the ability to list individual jobs from a workflow

## 0.2.0
* Standard output and error for factory jobs can be retrieved by specifying an instance id
* New command `prominence snapshot` allows users to create and retrieve a shapshot of a file or directory for a running job

## 0.1.25
* If no URL is available for an output file or directory, give a clear error message
* No longer set procsPerNode to the number of requested CPUs by default (if the actual number of CPUs per node is greater than what the user requested, we want to make use of them)
* (bug fix) Check for multiple nodes but no MPI flavour now works

## 0.1.24
* The `register` command made use of the json argument in the requests module when doing a post - changed this from json to data so that old versions of Python 2 will work

## 0.1.23
* Improve error messages when there are issues relating to device code flow initiation
* (bug fix) Workflows without dependencies were being being submitted to the /jobs API endpoint rather than /workflows
* Include policies section when describing jobs
* Specify preemptible & numberOfRetries in policies section of job json description
* Change numberOfRetries to maximumRetries in job json description
* Check token expiry date before contacting REST API
* Renamed `--constraint` option to `--placement`
* Add `--openmp-procs-per-node` as a shortcut which sets the MPI processes per node and OpenMP threads per node automatically
* Add `exec` command for running arbitrary commands in running jobs

## 0.1.22
* Handle DeletionError for `delete` command
* Allow output files & directories to be downloaded if job state is deleted or failed
* Show elapsed time of workflows
* Include factory (when necessary) when running `prominence describe workflow`
* Allow `intelmpi` as a choice of MPI type

## 0.1.21
* Report overall job maximum memory usage (maxMemoryUsageKB) for completed jobs

## 0.1.20
* Fixed bug for situation where `ls` returns no objects

## 0.1.19
* Added `rm` command for deleting objects from cloud storage

## 0.1.18
* If the environment variable PROMINENCE_SSL_VERIFY is set to "False", certificate verification will be disabled. This is for test purposes only.
* Report maximum resident set size

## 0.1.17
* Added `ls` command for listing objects in cloud storage
* File upload will now work on systems with old versions of the Python requests module (older than 2.4.2)

## 0.1.16
* Job and workflow creation will now work on systems with old versions of the Python requests module (older than 2.4.2)

## 0.1.15
* (bug fix) When listing multiple jobs the name of the last job was shown for all jobs
* Automatically create the ~/.prominence directory when running `login` - this is necessary for the case when the OIDC client id and secret are obtained from environment variables

## 0.1.14
* Allow OIDC client id and secret to be obtained from environment variables

## 0.1.13
* Handle situation if a job name is not defined
* Changes to ProminenceClient so that authentication from within a Jupyter notebook will work again

## 0.1.12
* Correction to file download required due to change from Swift to S3 API

## 0.1.11
* Numerous bug fixes

## 0.1.10
* Numerous bug fixes

## 0.1.9
* Code tidied up

## 0.1.6

* The JSON job definition for `prominence run` can now be either a URL or file
* Changes to error handling throughout code
* Improvements to ProminenceTask and ProminenceJob classes
* `--num` renamed as `--last`

## 0.1.5 

* Added a `register` command to register as an OIDC client
* Added a *mountpoint* option to artifacts so that a tarball can be made available inside a container at a specific mount point
* (bug fix) HTTP timeout for interactions with the PROMINENCE REST API now set correctly

## 0.1.4

* Added an option `--procs-per-node` for MPI jobs to specify the number of processes to run per node
* Handle minor change in API for retrieving standard output and error from jobs
* Handle an error in the client id or secret client id resulting in the first step of the device flow failing

## 0.1.3

* Add an option to specify B2DROP or OneData storage credentials
* Changed `create` to `run` and vice-versa

## 0.1.2

* (bug fix) Handling of version in setup.py which prevented requests module from being imported now corrected

## 0.1.1

* Handle changes in naming of job timing events
* Replace "IAM" with "OIDC" in environment variables

## 0.1.0

* The argument `--version` has been added
* The `create`, `list`, `describe`, `stdout`, and `stderr` commands now support both jobs and DAG workflows.
* The option `--mpi` has been replaced with `--openmpi` and `--mpich`, enabling support of both Open MPI and MPICH for MPI jobs.

## 0.0.8

* The ability to specify an MPI version has been removed, as this is no longer necessary.
* The preemptibility of a job is included in the output of the `describe` command.
