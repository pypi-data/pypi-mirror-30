"""
--- okta-user-id --

This is a simple module for turning (apparently) base62-encoded Okta user IDs
into UUIDs. It also allows for reversing the UUID to an Okta user ID.
"""

__title__ = 'okta-uuid'
__author__ = 'Travis Mehlinger'
__email__ = 'tmehlinger@gmail.com'
__version__ = '0.1.0'


import uuid

import base62


class OktaUserId(object):
    def __init__(self, uid):
        self.__uid = uid
        d = base62.decode(uid)
        b = d.to_bytes(16, byteorder='little')
        self.__uuid = u = uuid.UUID(bytes_le=b)

    @property
    def uid(self):
        return self.__uid

    @property
    def uuid(self):
        return self.__uuid

    def __eq__(self, other):
        return self.uid == other.uid

    def __str__(self):
        return self.uid

    def __repr__(self):
        return "OktaUserId('{}')".format(self.uid)

    @classmethod
    def from_uuid(cls, u, length=20):
        """
        Derive an Okta UID from the given UUID, padding the left of the string
        ID with zeroes.
        """
        b = int.from_bytes(u.bytes_le, byteorder='little')
        d = base62.encode(b)
        padded = d.zfill(length)
        return cls(padded)
