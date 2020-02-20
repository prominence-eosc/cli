class ProminenceError(Exception):
    """
    Base class for all PROMINENCE exceptions
    """
    pass

class ClientRegistrationError(ProminenceError):
    """
    Raised when client registration fails
    """
    pass

class ClientCredentialsError(ProminenceError):
    """
    Raised when there are problems with client credentials
    """
    pass

class TokenError(ProminenceError):
    """
    Raised when a token cannot be obtained
    """
    pass

class AuthenticationError(ProminenceError):
    """
    Raised when authentication fails
    """
    pass

class TokenExpiredError(ProminenceError):
    """
    Raised when a token has expired
    """
    pass

class ConnectionError(ProminenceError):
    """
    Raised when we cannot connect to the PROMINENCE server
    """
    pass

class JobCreationError(ProminenceError):
    """
    Raised when job submission fails
    """
    pass

class WorkflowCreationError(ProminenceError):
    """
    Raised when workflow submission fails
    """
    pass

class JobGetError(ProminenceError):
    """
    Raised when listing or describing a job fails
    """
    pass

class WorkflowGetError(ProminenceError):
    """
    Raised when listing or describing a workflow fails
    """
    pass

class DeletionError(ProminenceError):
    """
    Raised when deletion fails
    """
    pass

class FileUploadError(ProminenceError):
    """
    Raised when a file upload fails
    """
    pass

class StdStreamsError(ProminenceError):
    """
    Raised when there is a problem getting the standard output or error
    """
    pass

class IOError(ProminenceError):
    """
    Raised when there is a file read/write operation fails
    """
    pass

class ObjectError(ProminenceError):
    """
    Raised when there is an attempt to read/write objects fails
    """
    pass

class ExecError(ProminenceError):
    """
    Raised when there is an error executing a command inside a job
    """
    pass

class SnapshotCreateError(ProminenceError):
    """
    Raised when there is an error creating a snapshot
    """
    pass

class SnapshotGetErorr(ProminenceError):
    """
    Raised when there is an error getting a snapshot URL
    """
    pass

class UsageError(ProminenceError):
    """
    Raised when there is an error getting usage information
    """
    pass
