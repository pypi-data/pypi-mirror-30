import arrow
from urllib.parse import quote, unquote

from cargo import Model
from cargo.fields import UID, Timestamp, IP, Username, Array, Email,\
                         Key, Password, SmallInt, Bool

from cargo_users.exceptions import *
from cargo_users.fields import Settings
from cargo_users.utils import _HashUtil


__all__ = ('Users', 'LoginAttempts', 'IPJail')


class Users(Model, _HashUtil):
    """ ======================================================================
        ``Fields``
        ======================================================================
        - <:prop:uid> (#int) The universally unique identifier for this field.
        - <:prop:username> (#str) Screen name
        - <:prop:email> (#str) Email address
        - <:prop:password> (#str) Hashed password
        - <:prop:key> (#str) PRIVATE Access key used for authentication and
            unique token generation. It is absolutely critical that this key
            is never revealed to the public. In the event of key exposure,
            keys should be regenerated for affected users.
        - <:prop:oauth_providers> (#str) |provider_name$provider_id|
        - <:prop:join_ip> (:func:ipaddress.ip_address) the IP addressed used
            for signing up the account
        - <:prop:latest_ip> (:class:ipaddress.ip_address) the latest IP
            address to access the account
        - <:prop:join_date> (:class:arrow.Arrow) the date which the account
            was created on as a timestamp
        - <:prop:latest_login> (:class:arrow.Arrow) the last time a user
            logged into their account
        - <:prop:activated> (#bool) |True| if the account has been activated
            via some external validation method, e.g. email. See
            :meth:get_token, :meth:verify_token, and
            :func:cargo_users.activate for more information about activating
            accounts and to learn how to generate and verify tokens unique to
            individual users.
    """
    ORDINAL = ['uid', 'username', 'email', 'password', 'key',
               'oauth_providers', 'join_ip', 'latest_ip', 'join_date',
               'latest_login', 'activated']
    PRIVATE = ['password', 'key', 'join_ip', 'latest_ip']
    uid = UID()
    username = Username(index='btree', unique=True, not_null=True)
    email = Email(index='btree', unique=True, not_null=True)
    password = Password(minlen=8, not_null=True)
    key = Key(256, not_null=True)
    oauth_providers = Array(index='gin')
    join_ip = IP(not_null=True)
    latest_ip = IP(not_null=True)
    join_date = Timestamp(default=Timestamp.now(), not_null=True)
    latest_login = Timestamp(default=Timestamp.now(), not_null=True)
    activated = Bool(default=False, not_null=True)

    def __init__(self, *args, oauth_callback_url=None, oauth_providers=None,
                 **kwargs):
        """`Users Model`
            ==================================================================
            @oauth_callback_url: (#str) the base URL used for OAuth callbacks,
                e.g. |/users/oauth/callback| - this will be joined to the
                provider names given in @oauth_providers, e.g.
                for google |/users/oauth/callback/google|
            @oauth_providers: (#dict) OAuth providers with consumer keys,
                fields and scopes
                |{provider_name: {consumer_key: "", consumer_secret: ""}|
                e.g.
                ..
                providers = {
                  "facebook": {
                    "consumer_key": "PUBLIC_KEY",
                    "consumer_secret": "SECRET_KEY",
                    "scope": ["email", "user_birthday"],
                    "fields": ["id", "name", "email", "birthday", "gender"]
                  },
                  "twitter": {
                    "consumer_key": "PUBLIC_KEY",
                    "consumer_secret": "SECRET_KEY"
                  },
                  "google": {
                    "consumer_key": "PUBLIC_KEY",
                    "consumer_secret": "SECRET_KEY",
                    "scope": ["profile", "email"]
                  }
                }
                ..
            ==================================================================
            :see::meth:cargo.Model.__init__
            :see::meth:cargo.ORM.__init__
        """
        super().__init__(*args, **kwargs)
        self._oauth_providers = oauth_providers or {}
        self._oauth_callback_url = oauth_callback_url

    def __repr__(self):
        if getattr(self, 'username') and self.username is not None and\
           self.username.value_is_not_null:
            return '<%s:%s>' % (self.username, self.uid)
        else:
            return super().__repr__()

    def add_provider(self, name, **options):
        self._oauth_providers[name] = options

    def remove_provider(self, name):
        del self._oauth_providers[name]

    def _get_plain_token(self, expires):
        """ -> (#str) contents of token which the hash is based on """
        return '%s:%s' % (expires, self["key"])

    def get_token(self, size=24, ttl=86400):
        """ @size: (#int) length of the token in bytes, not including the
                16-byte salt, UID or expiration time. This number should
                probably not be any less than 16.
            @ttl: (#int) number of seconds to validate the token for
            -> (#str) A unique expireable token which will become invalid
               if a users' key is changed or the token expires.
        """
        expires = arrow.utcnow().timestamp + ttl
        hash = self._hash(self._get_plain_token(expires), size=size)
        return '%s$%s$%s' % (self.uid, expires, quote(hash, ''))

    def verify_token(self, hash):
        """ -> (#bool) Verifies a token from :meth:get_token belongs to
               this user
        """
        try:
            uid, expires, hash = hash.split('$')
        except ValueError:
            raise TokenError('This token is malformed.')
        if int(expires) < arrow.utcnow().timestamp:
            raise TokenError('This token has expired.')
        uid = int(uid)
        if self['uid'] != uid or not self['key']:
            model = self.filter(uid=uid).get()
        else:
            model = self
        if model is None:
            raise TokenError('No account is associated with this token.')
        return self._verify_hash(self._get_plain_token(expires), unquote(hash))

    def activate(self, token):
        """ Activates the user account belonging to @token and fills this
            model with the data attached to the user account
            -> (#bool) |True| if the account was activated
        """
        self.verify_token(token)
        self['activated'] = True
        return self.save()

    def fill_defaults(self, request=None, response=None):
        """ Fills default values for signing up """
        self.key.new()
        if request is not None:
            self.join_ip.from_request(request)
            self.latest_ip.from_request(request)

    def before_signup(self, request=None, response=None):
        """ Called before a user is signed up.
            Useful for pre-filling the model.
        """
        self.fill_defaults(request, response)

    def after_signup(self, request=None, response=None):
        """ Called after a user is signed up. """

    def before_login(self, request=None, response=None):
        """ Called before a user is signed up.
            Useful for pre-filling the model.
        """

    def after_login(self, request=None, response=None):
        """ Called after a user is logged in. """
        latest_login = self.latest_login.eq(self.latest_login.now())
        self.latest_ip.from_request(request)
        self.update(self.latest_ip, latest_login, self.password)

    def copy(self, *args, clear=False, **kwargs):
        return super().copy(*args,
                            oauth_providers=self._oauth_providers,
                            oauth_callback_url=self._oauth_callback_url,
                            clear=clear,
                            **kwargs)


class LoginAttempts(Model):
    ORDINAL = ('ip', 'tally', 'latest')
    ip = IP(primary=True, not_null=True)
    tally = SmallInt(default=0, not_null=True)
    latest = Timestamp(default=Timestamp.now(), index=True, not_null=True)

    def incr(self, count=1, ip=None):
        if ip is not None:
            self.where(self.ip.eq(ip))
        try:
            result = self.one().update(self.tally.incr(count),
                                       self.latest.eq(Timestamp.now()))
            assert result
            return result
        except:
            self.values(ip or self['ip'], count)
            return self.insert(self.ip, self.tally)


class IPJail(Model):
    ORDINAL = ('ip', 'lock_date')
    ip = IP(primary=True, not_null=True)
    lock_date = Timestamp(default=Timestamp.now(), index=True,
                          not_null=True)
