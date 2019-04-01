# Change Log

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
