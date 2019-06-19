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

class AuthenticationFailure(ProminenceError):
    """
    Raised when authentication fails
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
    Raised when a job list or describe fails
    """
    pass

class WorkflowGetError(ProminenceError):
    """
    Raised when a workflow list or describe fails
    """
    pass

class DeletionError(ProminenceError):
    """
    Raised when job/workflow deletion fails
    """
    pass

class FileUploadError(ProminenceError):
    """
    Raised when file upload fails
    """
    pass

class StdStreamsError(ProminenceError):
    """
    Raised when getting standard out/err fails
    """
    pass
