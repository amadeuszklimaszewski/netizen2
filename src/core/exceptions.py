class AlreadyExistsError(Exception):
    pass


class DoesNotExistError(Exception):
    pass


class AlreadyActiveError(Exception):
    pass


class UserNotActiveError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class TokenExpiredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass
