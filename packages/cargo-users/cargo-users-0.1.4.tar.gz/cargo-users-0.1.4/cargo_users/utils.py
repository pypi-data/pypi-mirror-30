import argon2
from vital.security import randkey

from cargo_users.exceptions import *


__all__ = ('_HashUtil',)


class _HashUtil(object):
    HASH_MEMORY_COST, HASH_TIME_COST, HASH_PARALLELISM = 1 << 5, 1, 1

    def _hash(self, string, size=24):
        hash = argon2.low_level.hash_secret(
            string.encode(),
            randkey(96).encode(),
            time_cost=self.HASH_TIME_COST,
            memory_cost=self.HASH_MEMORY_COST,
            parallelism=self.HASH_PARALLELISM,
            hash_len=size,
            type=argon2.low_level.Type.I,
            version=argon2.low_level.ARGON2_VERSION)
        return "$".join(hash.decode('utf-8').split("$")[-2:])

    def _verify_hash(self, string, hash):
        """ Verifies @string against @hash """
        try:
            hashargs = argon2.low_level.hash_secret(
                string.encode(),
                b'abcdefghijklmnopqrstuvwxyz',
                time_cost=self.HASH_TIME_COST,
                memory_cost=self.HASH_MEMORY_COST,
                parallelism=self.HASH_PARALLELISM,
                hash_len=16,
                type=argon2.low_level.Type.I,
                version=argon2.low_level.ARGON2_VERSION
            )
            hashargs = '$'.join(hashargs.decode('utf-8').split('$')[:-2])
            hash = (hashargs + '$' + hash).encode('utf-8')
            return argon2.low_level.verify_secret(hash,
                                                  string.encode('utf-8'),
                                                  type=argon2.low_level.Type.I)
        except argon2.exceptions.VerificationError:
            raise AuthTokenError("The supplied token was invalid.")
