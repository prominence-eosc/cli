# Change Log

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
