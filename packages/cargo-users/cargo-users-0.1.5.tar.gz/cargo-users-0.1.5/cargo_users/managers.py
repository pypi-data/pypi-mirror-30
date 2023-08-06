import arrow
from urllib.parse import urlparse

from cargo.exceptions import *

from cargo_users.exceptions import *
from cargo_users.models import LoginAttempts
from cargo_users.utils import _HashUtil

__all__ = (
    'AuthenticateOAuth',
    'UserCookies',
    'Authenticate',
)


class BaseUserManager(object):
    __slots__ = ('model',)

    def __init__(self, model):
        """ @model: (:class:Model) """
        self.model = model

    def clear(self):
        """ Clears the local model """
        self.model.clear()

    def reset(self):
        """ Resets and clears the local model state/fields """
        self.model.reset()


class UserCookies(object):
    __slots__ = ('request', 'response', 'cookies', 'prefix', 'options')

    def __init__(self, request, response, prefix='_c', **cookie_options):
        """`User Cookie Manager`
            ==================================================================
            @request: WSGI request context
            @response: WSGI request context
            @prefix: (#str) cookie name prefix
            @**cookie_options: keyword arguments passed to :class:SimpleCookie
                as options
        """
        self.request = request
        self.response = response
        self.prefix = prefix
        self.options = cookie_options
        self.options['httponly'] = True

    def _get_opt(self):
        opt = self.options
        if opt.get('expires'):
            del opt['expires']
        if not opt.get('path'):
            opt['path'] = '/'
        if not opt.get('domain'):
            opt['domain'] = '.%s' % self.request.referer.netloc
        return opt

    def get_name(self, type):
        return "%s%s" % (self.prefix, type)

    def set(self, name, value, expires=None):
        opt = self._get_opt()
        self.response.set_cookie(self.get_name(name), value, **opt)

    def get(self, name):
        return self.request.get_cookie(self.get_name(name),
                                       secret=self.options.get('secret'))

    def delete(self, name):
        opt = self._get_opt()
        self.response.delete_cookie(self.get_name(name), **opt)


class BaseRestManager(BaseUserManager, _HashUtil):
    __slots__ = ('model', 'request', 'response')

    def __init__(self, model, request, response):
        """ @model: (:class:Model)
            @request: WSGI request context
            @response: WSGI request context
        """
        super().__init__(model)
        self.request = request
        self.response = response


class Authenticate(BaseRestManager):
    __slots__ = ('max_attempts', 'model', 'request', 'response', 'attempts',
                 'cookies')
    IDENTITY_CODE = 1001
    SPAM_CODE = 1002
    PASSWORD_CODE = 1003
    KEY_NAME = 'k'
    ID_NAME = 'i'
    EXPIRES_NAME = 'e'
    # TODO: two-factor authentication with TOTP/HOTP w/ cryptography package

    def __init__(self, model, request, response, max_attempts=100,
                 cookie=None, attempts_model=None):
        """`Authentication Manager`
            ==================================================================
            @model: (:class:Model)
            @request: WSGI request context
            @response: WSGI request context
            @max_attempts: (#int) Maximum number of login tries to allow for
                a given IP address
            @cookie: (#dict) cookie options to pass to :class:SimpleCookie
            @attempts_model: (:class:LoginAttempts) initiated login attempts
                model
        """
        super().__init__(model, request, response)
        self.max_attempts = max_attempts
        if isinstance(cookie, UserCookies):
            self.cookies = cookie
        else:
            self.cookies = UserCookies(request, response, **(cookie or {}))
        self.attempts = attempts_model or \
            LoginAttempts(client=model.client,
                          schema=model.schema,
                          debug=model._debug)

    @property
    def token(self):
        """ The public authentication token """
        return self.get_cookie(self.KEY_NAME)

    def new_public_token(self, expires=0):
        """ Creates public token for user's authentication cookie, which is
            time-dependent and expires periodically.
        """
        token = self._hash("%s:%s" % (self.model['key'], expires))
        return token

    def set_cookies(self, remember_me=False):
        """ Sets the authorization cookies """
        if remember_me:
            expires = arrow.utcnow().timestamp + (60 * 60 * 24 * 365)
        else:
            expires = 0
        self.cookies.set(self.KEY_NAME, self.new_public_token(expires))
        self.cookies.set(self.ID_NAME, self.model['uid'])
        self.cookies.set(self.EXPIRES_NAME, expires)

    def get_cookies(self):
        """ Gets the authorization cookies """
        key = self.cookies.get(self.KEY_NAME)
        uid = self.cookies.get(self.ID_NAME)
        expires = self.cookies.get(self.EXPIRES_NAME)
        if key is not None and uid is not None and expires is not None:
            return (key, uid, expires)
        return (key, None, None)

    def delete_cookies(self):
        """ Deletes the authorization cookies """
        self.cookies.delete(self.KEY_NAME)
        self.cookies.delete(self.ID_NAME)
        self.cookies.delete(self.EXPIRES_NAME)

    def logged_in(self, model=None):
        """ Checks whether or not a user is logged in
            -> (#bool) |True| if @model is logged in based on the request
               cookies
        """
        key, uid, expires = self.get_cookies()
        if key is None or uid is None or expires is None:
            return False
        model = model or self.model
        model['uid'] = uid
        model = model.get(model.key)
        if model is None:
            return False
        verify = "%s:%s" % (model['key'], expires)
        try:
            return self._verify_hash(verify, key)
        except AuthTokenError:
            return False
        return False

    def _tally_attempts(self):
        """ Tallies the number of login attempts made by an IP address """
        self.attempts.ip.from_request(self.request)
        self.attempts.get()
        if self.attempts.tally.value_is_not_null and \
           self.attempts['tally'] > self.max_attempts:
            raise AuthError('You are temporarily banned from logging in '
                            'because you have exceeded the maximum number of '
                            'failed attempts.',
                            code=self.SPAM_CODE)

    def login(self, **data):
        """ Logs a user in
            -> (:class:Model) if the login attempt is successful, otherwise
               raises :class:AuthError
        """
        self._tally_attempts()
        if (data.get('username') is None and data.get('email') is None)\
           or data.get('password') is None:
               raise AuthError('This username or email address was not found.',
                               code=self.IDENTITY_CODE)
        try:
            self.model.fill(username=data['username'])
        except KeyError:
            try:
                self.model.fill(email=data['email'])
            except KeyError:
                pass
        self.model.before_login(self.request, self.response)
        model = self.model.get()

        if model is None:
            raise AuthError('This username or email address was not found.',
                            code=self.IDENTITY_CODE)
        try:
            model.password.verify_and_migrate(data['password'])
            self.model = model
            self.set_cookies(remember_me=data.get('remember_me', False))
            result = model
            model.after_login(self.request, self.response)
        except (IncorrectPasswordError, KeyError):
            result = None
            self.attempts.incr()
            raise AuthError('The provided password was incorrect.',
                            code=self.PASSWORD_CODE)
        return result

    def logout(self):
        """ Logs a user out """
        self.delete_cookies()


class AuthenticateOAuth(Authenticate):
    __slots__ = ('max_attempts', 'model', 'request', 'response', 'attempts',
                 'cookies')

    def login(self, remember_me=True):
        """ Logs a user in
            -> (:class:Model) if the login attempt is successful, otherwise
               raises :class:AuthError
        """
        self.model.before_login(self.request, self.response)
        self.set_cookies(remember_me=remember_me)
        result = self.model
        self.model.after_login(self.request, self.response)
        return result
