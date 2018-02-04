import regex

from configuration import C
from directory import Directory

class User:

    def __init__(self, name):
        if len(name) < 3:
            raise ValueError()
        if len(name) > 8:
            raise ValueError()
        if regex.match("[a-z]", name[0]) is None:
            raise ValueError()
        if regex.fullmatch("[a-z0-9]*", name[1:]) is None:
            raise ValueError()
        self._name = name

    def dn(self):
        return Directory.dn(C.DOMAIN, self._name)

    def directory(self, password):
        return Directory(self.dn(), password)

    def get(self):
        query = "(uid=%s)" % self._name
        reader = Directory().reader("person", query=query)
        return reader.search()[0].entry_writable()

    def create(self, password, mail, display_name, first_name, last_name, tidy_contact_number=None):
        entry = Directory().writer("person").new(self.dn())
        entry.uid = self._name
        entry.cn = self._name
        entry.userPassword = password
        entry.mail = mail
        entry.displayName = display_name
        entry.givenName = first_name
        entry.sn = last_name
        entry.homeDirectory = "/home/%s" % self._name
        entry.loginShell = "/bin/zsh"
        entry.memberUid = self._name
        if tidy_contact_number is not None:
            entry.neatTidyContactNumber = tidy_contact_number
        next = User.next()
        entry.uidNumber = next
        entry.gidNumber = next
        entry.entry_commit_changes()

    @staticmethod
    def authenticate(username, password):
        result = User(username)
        result.directory(password)
        return result

    @staticmethod
    def next():
        reader = Directory().reader("club")
        entry = reader.search()[0].entry_writable()
        result = entry.neatNextUidNumber.value
        entry.neatNextUidNumber = result + 1
        entry.entry_commit_changes()
        return result

    @staticmethod
    def new(what, reservations=None):
        result = None
        while result is None:
            try:
                candidate = User(input("%s username: " % what))
                if reservations is not None:
                    if candidate._name in reservations:
                        raise ValueError()
                result = candidate
            except ValueError:
                print("\nPlease try again.")
        return result._name
