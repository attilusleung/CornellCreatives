class InvalidServiceError(RuntimeError):
    pass

class InvalidTokenError(RuntimeError):
    pass

class NoTokenError(RuntimeError):
    pass

class ExpiredTokenError(RuntimeError):
    pass
