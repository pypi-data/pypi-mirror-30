import functools

from cargo.exceptions import *
from cargo_users.exceptions import *
from cargo_users.managers import Authenticate
from cargo_users.oauth import get_provider


__all__ = (
    'activate',
    'authenticate',
    'authorize',
    'login',
    'logout',
    'oauth_authorize',
    'oauth_callback',
    'require_password',
    'require_activation',
    'signup'
)


def activate(model, request, response, raises=False, **kwargs):
    """ User account activation decorator
        @model: (:class:Model)
        @request: WSGI request context
        @response: WSGI request context
        @raises: (#bool) |True| to allow :class:TokenError to raise
        @kwargs are passed to :class:Authenticate
        -> (:class:Users) if the login is successful, otherwise returns
           the exception which was raised

        ..
        @route('/users/activate?token={token}')
        @activate(Users(), request, response)
        def activate_user(user):
            request.session.user = user
        ..
    """
    def do_activate(obj):
        @functools.wraps(obj)
        def _do_activate(token):
            auth = Authenticate(model.clear_copy(), request, response,
                                **kwargs)

            try:
                activated = auth.model.activate(token)
            except TokenError as e:
                if raises:
                    raise
                activated = e
            return obj(activated)

        return _do_activate

    return do_activate


def authenticate(model, request, response, on_reject=None, **kwargs):
    """ User authentication decorator. Requires that a user be logged in
        in order to proceed. A user is logged in when they possess the correct
        cookies. If a user cannot be authenticated, a 403 Forbidden status code
        is added to the response.
        @model: (:class:Model)
        @request: WSGI request context
        @response: WSGI request context
        @status_code: (#int) status code to set in the response
        @on_reject: (#callable) called when authentication fails and returns
            the result of. Must accept all of the arguments passed to @func.
        @**kwargs: keyword arguments passed to :class:Authenticate
        -> the result of the wrapped function, the result of @on_reject,
           otherwise |False|
        ..
        @route('/follow/{uid}')
        @authenticate(Users(), request, response)
        def follow_user(model, uid):
            Followers.add(actor=request.session.user['uid'], target=uid)
        ..
    """
    def do_authenticate(obj):
        @functools.wraps(obj)
        def _do_authenticate(*args, **kwargs):
            auth = Authenticate(model.clear_copy(), request, response,
                                **kwargs)
            if auth.logged_in() is True:
                return obj(auth.model, *args, **kwargs)
            return obj(False, *args, **kwargs) if on_reject is None else \
                on_reject(auth.model, *args, **kwargs)

        return _do_authenticate

    return do_authenticate


def authorize(auth_func, on_reject=None):
    """ User authorization decorator. Requires that a user be logged in
        in order to proceed. A user is logged in when the function supplied
        in @auth_func returns |True|.
        @auth_func: (#callable) must return |True| to authorize a user
            to continue
        @status_code: (#int) status code to set in the response
        @on_reject: (#callable) called when authorization fails and returns
            the result of. Must accept all of the arguments passed to
            @auth_func.
        -> the result of the wrapped function, the result of @on_reject,
           otherwise |False|
        ..
        @route('/follow/{uid}')
        def follow_user(uid):
            @authorize(session.user.is_logged_in,
                       on_reject=lambda uid: response.set_status(503))
            def do_follow():
                Followers.add(actor=request.session.user['uid'], target=uid)
        ..
    """
    def do_authorize(obj):
        @functools.wraps(obj)
        def _do_authorize(*args, **kwargs):
            if auth_func() is True:
                return obj(*args, **kwargs)

            return False if on_reject is None else on_reject(*args, **kwargs)

        return _do_authorize

    return do_authorize


def login(model, request, response, *args, raises=False, **kwargs):
    """ User login decorator
        @model: (:class:Model)
        @request: WSGI request context
        @response: WSGI request context
        @raises: (#bool) |True| allows :class:QueryError and
            :class:ValidationError to raise, otherwise these exceptions
            are returned as the result
        @args and @kwargs are passed to :class:Authenticate
        -> (:class:Users) if the login is successful, otherwise returns
           :class:AuthError
        ..
        @route('/users/login')
        @login(Users(), request, response)
        def login_user(user):
            request.session.user = user
        ..
    """
    def do_login(obj):
        @functools.wraps(obj)
        def _do_login():
            auth = Authenticate(model.clear_copy(), request, response,
                                **kwargs)

            try:
                result = auth.login(**request.post)
            except AuthError as e:
                if raises:
                    raise
                result = e

            return obj(result)

        return _do_login

    return do_login


def logout(model, request, response, *args, **kwargs):
    """ User logout decorator
        @model: (:class:Model)
        @request: WSGI request context
        @response: WSGI request context
        @args and @kwargs are passed to :class:Authenticate
        ..
        @route('/users/logout')
        @logout(Users(), request, response)
        def logout_user():
            del request.session.user
        ..
    """
    def do_logout(obj):
        @functools.wraps(obj)
        def _do_logout():
            auth = Authenticate(model.clear_copy(), request, response,
                                **kwargs)
            auth.logout()
            return obj()

        return _do_logout

    return do_logout


def oauth_authorize(model, request, response, cookie=None, service=None):
    """ OAuth authorizer decorator. Must provide a keyword argument for
        'provider' which represents the provider name of the OAuth service.
        @model: (:class:Model)
        @request: WSGI request context
        @response: WSGI request context
        ..
        users = Users(oauth_callback_url=callback_url,
                      oauth_providers=providers)

        @route('/users/oauth/authorize/{provider}')
        @oauth_authorize(users, request, response)
        def oauth_user_authorize(oauth):
            return redirect(oauth.authorize_url)
        ..
    """
    def do_oauth(obj):
        @functools.wraps(obj)
        def _do_oauth(provider):
            if provider not in model._oauth_providers:
                raise OAuthError('Provider `%s` not found in `%s` model.' %
                                 (provider, model.__class__))

            try:
                return obj(service)
            except NameError:
                url = model._oauth_callback_url
                service = get_provider(provider,
                                       request=request,
                                       response=response,
                                       base_callback_url=url,
                                       cookie=cookie,
                                       **model._oauth_providers[provider])
                return obj(service)

        return _do_oauth

    return do_oauth


def oauth_callback(model, request, response, service=None, **session_args):
    """ OAuth callback decorator
        ..
        @route('/users/oauth/callback/{provider}')
        @oauth_callback(Users(), request, response)
        def oauth_user_callback(oauth, user):
            if user is None:
                signup(oauth)
            else:
                redirect(...)
        ..
    """
    def do_oauth(obj):
        @functools.wraps(obj)
        def _do_oauth(provider):
            if provider not in model._oauth_providers:
                raise OAuthError('Provider `%s` not found in `%s` model.' %
                                 (provider, model.__class__))

            #: Calls back OAuth
            try:
                service.callback(**session_args)
            except NameError:
                url = model._oauth_callback_url
                service = get_provider(provider,
                                       request=request,
                                       response=response,
                                       base_callback_url=url,
                                       **model._oauth_providers[provider])
                service.callback(**session_args)

            #: Finds the user if they are already signed up
            mod = model.clear_copy()
            mod.filter(oauth_providers__contains=[service.key])
            user = mod.get()

            if user is not None:
                #: Updates the users' credentials and logs them in
                user.before_login(request, response)
                auth = Authenticate(user, request, response)
                auth.set_cookies()
                user.after_login(request, response)

            return obj(service, user)

        return _do_oauth

    return do_oauth


def require_password(user, request, response, on_reject=None):
    """ Requires a password and unique identifier to be passed along with the
        request post data in order to proceed
        @user: (:class:Users) a filled user model to verify the password from
            the request post data with
        @request: WSGI request context
        @response: WSGI request context
        @status_code: (#int) status code to set in the response
        @on_reject: (#callable) called when authentication fails and returns
            the result of. Must accept all of the arguments passed to the
            wrapped function.
        -> the result of the wrapped function, the result of @on_reject,
           otherwise |None|
        ..
        @route('/users/edit')
        def edit_user_data():
            @require_password(request.session['user'], request, response)
            def do_edit():
                ...
        ..
    """
    def do_require(obj):
        @functools.wraps(obj)
        def _do_require(*args, **kwargs):
            try:
                assert user.password.verify(request.post['password'])
            except (KeyError, IncorrectPasswordError, AssertionError):
                return None if on_reject is None else \
                    on_reject(*args, **kwargs)
            return obj(*args, **kwargs)
        return _do_require

    return do_require


def require_activation(user, request, response, on_reject=None):
    """ Requires a user's account to be activated in order to continue
        ..
        @route('/users/edit')
        def edit_user_data():
            @require_activation(request.session['user'], request, response)
            def do_edit():
                ...
        ..
    """
    def do_require(obj):
        @functools.wraps(obj)
        def _do_require(*args, **kwargs):
            if user['activated'] is True:
                return obj(*args, **kwargs)
            return None if on_reject is None else on_reject(*args, **kwargs)
        return _do_require

    return do_require


def signup(model, request, response, raises=False, **kwargs):
    """ User signup decorator
        @model: (:class:Model)
        @request: WSGI request context
        @response: WSGI request context
        @raises: (#bool) |True| allows :class:QueryError and
            :class:ValidationError to raise, otherwise these exceptions
            are returned as the result
        @kwargs are passed to :class:Authenticate
        -> (:class:Users) if the signup is successful, otherwise
           returns the exception raised
        ..
        @route('/users/signup')
        @signup(Users(), request, response)
        def signup_user(user):
            request.session.user = user
        ..
    """
    model = model.clear_copy()

    def do_signup(obj):
        @functools.wraps(obj)
        def _do_signup():
            mod = model.clear_copy()
            data = {k: v
                    for k, v in request.post.items()
                    if k in mod.field_names}
            mod.fill(**data)
            mod.before_signup(request, response)
            exists = False
            if mod.best_unique_index:
                exists = mod.where(mod.best_unique_index).get()
            try:
                if exists:
                    raise DuplicateError('This username or email address '
                                         'is already being used. Please '
                                         'select a different one.')
                result = mod.insert()
                mod.after_signup(request, response)
                auth = Authenticate(model.clear_copy(), request, response,
                                    **kwargs)
                auth.login()
            except (QueryError, ValidationError, DuplicateError) as e:
                if raises:
                    raise
                result = e
            return obj(result)
        return _do_signup

    return do_signup
