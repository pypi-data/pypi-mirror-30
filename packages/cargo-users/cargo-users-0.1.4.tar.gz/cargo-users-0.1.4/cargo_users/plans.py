from cargo.builder import Plan, create_function, create_trigger
from cargo.exceptions import QueryError
from cargo_users.models import *


__all__ = ('UsersPlan', 'LoginAttemptsPlan', 'IPJailPlan')


class UsersPlan(Plan):
    
    def __init__(self, model=None, **kwargs):
        model = model or Users()
        super().__init__(model, **kwargs)


_expire_function = """
$$
BEGIN
    -- Deletes rows from @table which are older than @interval
    DELETE FROM {table} WHERE {field} < now() - INTERVAL '{interval}';
    RETURN NULL;
END;
$$
"""


class LoginAttemptsPlan(Plan):
    expire_in = '30 minutes'

    def __init__(self, model=None, **kwargs):
        model = model or LoginAttempts()
        super().__init__(model, **kwargs)

    def after(self):
        name = 'expire_%s_rows' % self.model.table
        func = '%s()' % name
        try:
            #: Creates function for expiring stale attempts
            create_function(self.model,
                            func,
                            _expire_function.format(
                                table=self.model.table,
                                field=self.columns.latest._common_name,
                                interval=self.expire_in),
                            returns='trigger',
                            language='plpgsql')
        except QueryError as e:
            print('Warning:', e)
        try:
            #: Creates triger for expiring stale attempts
            create_trigger(self.model,
                           '%s_trigger' % name,
                           'AFTER',
                           'INSERT',
                           'UPDATE',
                           table=self.model.table,
                           type='STATEMENT',
                           function=func)
        except QueryError as e:
            print('Warning:', e)


class IPJailPlan(Plan):

    def __init__(self, model=None, **kwargs):
        model = model or IPJail()
        super().__init__(model, **kwargs)


def execute(**kwargs):
    UsersPlan(**kwargs).execute()
    LoginAttemptsPlan(**kwargs).execute()
    IPJailPlan(**kwargs).execute()
