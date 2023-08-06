"""

  `OAuth Services`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2016 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
import copy
from collections import UserDict
import dateutil.parser
from io import BytesIO

try:
    import ujson as json
except ImportError:
    import json

from urllib.parse import urljoin, parse_qsl

from vital.cache import memoize
from vital.tools import strings as string_tools
from vital.security import randkey

from rauth import OAuth1Service, OAuth2Service
import requests

from cargo_users.exceptions import *


__all__ = (
    'get_provider',
    'OAuth',
    'OAuth1',
    'OAuth2',
    'FacebookOAuth',
    'GoogleOAuth',
    'TwitterOAuth',
    'LinkedInOAuth'
)


def oauth_bytes_decode(data):
    return json.loads(data.decode("utf-8"))


def get_provider(name, **kwargs):
    for cls_ in OAuth.__subclasses__():
        for cls in cls_.__subclasses__():
            if name == cls.PROVIDER:
                return cls(**kwargs)
    raise OAuthError('Could not find a provider named `%s`.' % name)


class OAuth(UserDict):
    PROVIDER = None
    AUTHORIZE_URL = None
    ACCESS_TOKEN_URL = None
    BASE_URL = None
    SESSION_URI = None
    SCOPE_DELIM = ","

    def __init__(self,
                 *,
                 request=None,
                 response=None,
                 consumer_key=None,
                 consumer_secret=None,
                 base_callback_url=None,
                 scope=None,
                 cookie=None):
        ''' @cookie: (#dict) cookie options to pass to :class:SimpleCookie,
                defaults to {'httponly': True}
        '''
        self.request = request
        self.response = response
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self._callback_url = base_callback_url
        self.scope = scope or []
        self.data = {}
        self.service = None
        self.cookie = cookie or {'httponly': True}

    @property
    def callback_url(self):
        return urljoin(self._callback_url + '/', self.PROVIDER)

    @property
    def session_uri(self):
        return self.SESSION_URI

    @property
    def name(self):
        name = self.data['name'].split(" ")
        return [name[0], " ".join(name[1:])]

    @property
    def id(self):
        return self.data['id']

    @property
    def key(self):
        return '%s$%s' % (self.PROVIDER, self.data['id'])

    @property
    def username(self):
        username = self.data.get('screen_name', self.data.get('username'))
        if username:
            return string_tools.to_alnum(username)
        return None

    @property
    def gender(self):
        gender = self.data.get("gender")
        return gender.lower() if gender else gender

    @property
    def unique_username(self):
        return "{}{}".format(self.username, self.id[-4:])

    @property
    def email(self):
        return self.data.get('email', self.data.get('email_address'))

    @property
    def birthday(self):
        if self.data.get('birthday'):
            return dateutil.parser.parse(self.data['birthday'])

    def get_image(self):
        """ -> (#tuple(:class:BytesIO image content, #dict image headers)) """
        r = requests.get(self.image, stream=True, timeout=5)
        if r.status_code == 200:
            return (BytesIO(r.content), r.headers)
        return None

    @staticmethod
    def get_provider(name, **kwargs):
        return get_provider(name, **kwargs)

    def copy(self):
        return copy.copy(self)


class OAuth2(OAuth):

    def __init__(self, csrf_cookie_name='oauthcsrf', **kwargs):
        super().__init__(**kwargs)
        self.csrf_cookie_name = csrf_cookie_name
        self.service = OAuth2Service(
            name=self.PROVIDER,
            client_id=self.consumer_key,
            client_secret=self.consumer_secret,
            authorize_url=self.AUTHORIZE_URL,
            access_token_url=self.ACCESS_TOKEN_URL,
            base_url=self.BASE_URL
        )

    @property
    def authorize_url(self):
        return self.service.get_authorize_url(
            scope=self.SCOPE_DELIM.join(self.scope),
            response_type='code',
            redirect_uri=self.callback_url,
            state=self.get_state())

    def get_state(self):
        state = randkey(128)
        self.response.set_cookie(self.csrf_cookie_name, state, **self.cookie)
        return state

    @property
    def state_cookie(self):
        return self.request.get_cookie(self.csrf_cookie_name)

    def callback(self, data=None, **session_args):
        """ @data: #dict to update the :meth:OAuth2Service:get_auth_session
                'data' argument with
            -> #dict of user info """
        if 'code' not in self.request.query:
            raise OAuthCallbackError("Required parameter `code` not found in "
                                     "the request URI.")

        if 'state' not in self.request.query:
            raise OAuthCallbackError("Required parameter `state` not found in "
                                     "the request URI.")
        elif self.state_cookie != self.request.query['state']:
            raise OAuthCallbackError("The request parameter `state` did not "
                                     "match the OAuth CSRF cookie.")

        _data = {'code': self.request.query['code'],
                 'grant_type': 'authorization_code',
                 'redirect_uri': self.callback_url}
        if data:
            _data.update(data)

        oauth_session = self.service.get_auth_session(data=_data,
                                                      **session_args)
        self.data = oauth_session.get(self.session_uri).json()

        return self.data


class OAuth1(OAuth):
    PROVIDER = None
    REQUEST_TOKEN_URL = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OAuth1Service(
            name=self.PROVIDER,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            request_token_url=self.REQUEST_TOKEN_URL,
            authorize_url=self.AUTHORIZE_URL,
            access_token_url=self.ACCESS_TOKEN_URL,
            base_url=self.BASE_URL
        )

    @property
    def authorize_url(self):
        request_token = self.service.get_request_token(params={
            'oauth_callback': self.callback_url
        })
        self.response.set_cookie('_ort',
                                 json.dumps(request_token),
                                 **self.cookie)
        return self.service.get_authorize_url(request_token[0])

    def callback(self, data=None, decoder=None, **session_args):
        request_token, request_token_secret = \
            json.loads(self.request.get_cookie('_ort'))

        if 'oauth_verifier' not in self.request.query:
            raise OAuthCallbackError('Required parameter `oauth_verifier` not '
                                     'found in the request URI.')

        _data = {'oauth_verifier': self.request.query['oauth_verifier']}

        if data:
            _data.update(data)

        try:
            oauth_session = self.service.get_auth_session(request_token,
                                                          request_token_secret,
                                                          decoder=decoder,
                                                          data=_data)
        except KeyError:
            self.response.delete_cookie('_ort')
            raise

        self.data = oauth_session.get(self.session_uri, **session_args).json()
        return self.data


class FacebookOAuth(OAuth2):
    PROVIDER = 'facebook'
    AUTHORIZE_URL = 'https://graph.facebook.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
    BASE_URL = 'https://graph.facebook.com/v2.4/'
    SESSION_URI = 'me'

    def __init__(self, *, fields=None, **kwargs):
        super().__init__(**kwargs)
        self.fields = fields or ['id', 'name']

    @property
    def session_uri(self):
        return self.SESSION_URI + "?fields=" + ",".join(self.fields)

    @property
    def image(self):
        return urljoin(self.BASE_URL, self.id + '/picture?type=large')
    # @property
    # def image(self):
    #     return self.data.get('picture')
    def callback(self, *args, **session_args):
        session_args.update({'decoder': json.loads})
        return super().callback(*args, **session_args)
        

class GoogleOAuth(OAuth2):
    PROVIDER = 'google'
    AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
    ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    BASE_URL = 'https://www.googleapis.com/oauth2/v1/'
    SESSION_URI = 'userinfo'
    SCOPE_DELIM = " "

    @property
    def image(self):
        return self.data.get('picture')

    def callback(self, *args, **session_args):
        session_args.update({'decoder': json.loads})
        return super().callback(*args, **session_args)


class TwitterOAuth(OAuth1):
    PROVIDER = 'twitter'
    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    AUTHORIZE_URL = 'https://api.twitter.com/oauth/authenticate'
    ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
    BASE_URL = 'https://api.twitter.com/1.1/'
    SESSION_URI = 'account/verify_credentials.json'

    @property
    def username(self):
        return self.data['screen_name']

    @property
    def image(self):
        return self.data['profile_image_url_https'].replace("_normal", "")

    def callback(self, *args, **session_args):
        session_args.update({'params': {'include_email': True}})
        return super().callback(*args,
                                decoder=lambda x:
                                    dict(parse_qsl(x.decode('utf-8'))),
                                **session_args)



class LinkedInOAuth(OAuth2):
    PROVIDER = 'linkedin'
    AUTHORIZE_URL = 'https://www.linkedin.com/uas/oauth2/authorization'
    ACCESS_TOKEN_URL = 'https://www.linkedin.com/uas/oauth2/accessToken'
    BASE_URL = 'https://api.linkedin.com/v1/'
    SESSION_URI = 'people/~'
    SCOPE_DELIM = " "

    def __init__(self, fields=None, scope=None, **kwargs):
        scope = scope or ['r_basicprofile', 'r_fullprofile']
        super().__init__(scope=scope, **kwargs)
        self.fields = fields or ['id',
                                 'email-address',
                                 'formatted-name',
                                 'picture-url',
                                 'date-of-birth']

    @property
    def image(self):
        return self.data['pictureUrl']

    @property
    def email(self):
        return self.data['emailAddress']

    @property
    def session_uri(self):
        return '%s:(%s)?format=json' % (self.SESSION_URI, ','.join(self.fields))

    @property
    def name(self):
        name = self.data['formattedName'].split(" ")
        return [name[0], " ".join(name[1:])]

    @property
    def birthday(self):
        return self.data.get('dateOfBirth')

    def callback(self, *args, **session_args):
        session_args.update({'decoder': oauth_bytes_decode})
        return super().callback(*args, **session_args)
