# Change Log

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
