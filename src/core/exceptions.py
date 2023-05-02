class AuthenticationError(Exception):
    """Base class for all authentication errors."""


class InvalidAccessTokenError(AuthenticationError):
    """Raised when an access token is invalid."""


class ExpiredAccessTokenError(AuthenticationError):
    """Raised when an access token is expired."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when invalid credentials are provided."""


class PermissionDeniedError(AuthenticationError):
    """Raised when a user does not have permission to perform an action."""


class ApplicationError(Exception):
    """Base class for all application layer errors."""


class InvalidTokenError(ApplicationError):
    """Raised when a token is invalid."""


class ExpiredTokenError(ApplicationError):
    """Raised when a token is expired."""


class AlreadyExistsError(ApplicationError):
    """Raised when an entity already exists."""


class DoesNotExistError(ApplicationError):
    """Raised when an entity does not exist."""


class AlreadyActiveError(ApplicationError):
    """Raised when user is already active."""


class UserNotActiveError(ApplicationError):
    """Raised when user is not active."""


class NotAGroupMemberError(ApplicationError):
    """Raised when user is not a member of a group."""


class NotAGroupOwnerError(ApplicationError):
    """Raised when user is not an owner of a group."""


class NotAGroupOwnerOrAdminError(ApplicationError):
    """Raised when user is not an owner of a group or an admin."""


class CannotDeleteAGroupOwnerError(ApplicationError):
    """Raised when a user tries to delete a group owner."""


class CannotLeaveGroupAsOwnerError(ApplicationError):
    """Raised when a user tries to leave a group as an owner."""


class AlreadyAGroupMemberError(ApplicationError):
    """Raised when user is already a member of a group."""


class AlreadyAGroupOwnerError(ApplicationError):
    """Raised when user is already an owner of a group."""


class AlreadyRequestedToJoinGroupError(ApplicationError):
    """Raised when user has already requested to join a group."""


class RequestNotPendingError(ApplicationError):
    """Raised when a request has been accepted or declined."""


class NotARequestOwnerError(ApplicationError):
    """Raised when a user is not the owner of a request."""
