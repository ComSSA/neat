import ldap3
from ldap3.utils.conv import escape_bytes

from configuration import C

class Directory:

    def __init__(self, user=C.LDAP_MANAGER, password=C.LDAP_PASSWORD):
        self._server = ldap3.Server(C.LDAP_SERVER, 636, use_ssl=True)
        self._connection = ldap3.Connection(self._server, user, password)
        if not self._connection.bind():
            raise AuthenticationError()

    def schema(self, what):
        return ldap3.ObjectDef({
            "club": ["top", "organization", "dcObject", "neatClub"],
            "group": ["groupOfNames", "posixGroup"],
            "person": ["inetOrgPerson", "neatPersonAccount", "posixAccount", "posixGroup", "shadowAccount"]
        }[what], self._connection)

    def reader(self, schema, base=None, *args, **kwargs):
        if type(schema) is str:
            schema = self.schema(schema)
        if base is None:
            base = Directory.dn(C.DOMAIN)
        return ldap3.Reader(self._connection, schema, base, *args, **kwargs)

    def writer(self, schema, *args, **kwargs):
        if type(schema) is str:
            schema = self.schema(schema)
        return ldap3.Writer(self._connection, schema, *args, **kwargs)

    @staticmethod
    def dn(root, uid=None):
        result = ",".join("dc=%s" % i for i in C.DOMAIN.split("."))
        if uid is not None:
            # result = "uid=%s,ou=users,%s" % (escape_bytes(uid), result)
            result = "uid=%s,ou=users,%s" % (uid, result) # FIXME
        return result

class AuthenticationError(Exception):
    pass
