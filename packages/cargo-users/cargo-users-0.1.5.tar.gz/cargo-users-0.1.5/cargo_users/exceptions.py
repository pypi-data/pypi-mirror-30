class TokenError(Exception):
    """ Raised when a general user token is invalid """
    code = 1004


class AuthError(Exception):
    """ Raised when there is an error authenticating an account """
    code = 0
    def __init__(self, message, code=None):
        self.message = message
        self.code = code or self.code


class AuthTokenError(AuthError, TokenError):
    """ Raised when an autorization token is invalid """
    code = 1005


class OAuthError(AuthError):
    """ Raised when there is an error with OAuth authentication """
    code = 1006


class OAuthCallbackError(OAuthError):
    """ Raised when there is an error within the OAuth callback execution """
    code = 1007


class DuplicateError(Exception):
    """ Raised when someone tries to create an account with unique constraints
        which already exist.
    """
    code = 1008
    def __init__(self, message, code=None):
        self.message = message
        self.code = code or self.code
