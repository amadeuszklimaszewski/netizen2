class AuthenticationError(Exception):
    pass


class InvalidAccessTokenError(AuthenticationError):
    pass


class ExpiredAccessTokenError(AuthenticationError):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class PermissionDeniedError(AuthenticationError):
    pass


class ApplicationError(Exception):
    pass


class InvalidTokenError(ApplicationError):
    pass


class ExpiredTokenError(ApplicationError):
    pass


class AlreadyExistsError(ApplicationError):
    pass


class DoesNotExistError(ApplicationError):
    pass


class AlreadyActiveError(ApplicationError):
    pass


class UserNotActiveError(ApplicationError):
    pass
