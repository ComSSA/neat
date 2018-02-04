from getpass import getpass

import regex
import bcrypt

from configuration import C

class Password:

    def __init__(self, string):
        if len(string) < 10:
            raise ValueError()
        if len(string) > 72:
            raise ValueError()
        if regex.fullmatch("[ -~]*", string) is None:
            raise ValueError()
        self._string = string

    def hash(self, full=False):
        result = bcrypt.hashpw(self._string.encode(), bcrypt.gensalt(13)).decode()
        if full:
            result = "{CRYPT}%s" % result
        return result

    @staticmethod
    def ask(what, old=None, username=None):
        if old is not None:
            print("\nPlease try again.")
        if username is None:
            username = input("%s username: " % what)
        else:
            print("%s username: %s" % (what, username))
        password = getpass("%s password: " % what)
        return (username, password)

    @staticmethod
    def new(test=None):
        result = None
        while result is None:
            try:
                one = Password(getpass("New password: "))
                two = Password(getpass("Now confirm: "))
                if one._string != two._string:
                    raise ValueError()
                result = one
            except ValueError:
                print("\nPlease try again.")
        return result.hash(True)
