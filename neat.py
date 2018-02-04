import sys
import traceback
import importlib
import readline

from ldap3.core.exceptions import LDAPPasswordIsMandatoryError

from configuration import C
from directory import Directory, AuthenticationError
from user import User
from password import Password

def out(*args, **kwargs):
    print(file=sys.stderr, *args, **kwargs)

def scan(prompt, *args, **kwargs):
    out(prompt, end="")
    return input()

def parse(command):
    state = "none"
    result = []
    next = ""
    for i in command:
        if state == "none":
            if i in "\\":
                state = "some escape"
            elif i == "'":
                state = "single"
            elif i == '"':
                state = "double"
            elif i in "\b\t\n\v\f\r ":
                pass
            else:
                state = "some"
                next += i
        elif state == "some":
            if i in "\\":
                state = "some escape"
            elif i == "'":
                state = "single"
            elif i == '"':
                state = "double"
            elif i in "\b\t\n\v\f\r ":
                state = "none"
                result += [next]
                next = ""
            else:
                next += i
        elif state == "some escape":
            state = "some"
            next += i
        elif state == "single":
            if i == "'":
                state = "some"
            else:
                next += i
        elif state == "double":
            if i == '"':
                state = "some"
            elif i == "\\":
                state = "double escape"
            else:
                next += i
        elif state == "double escape":
            state = "double"
            if i == '"':
                next += '"'
            elif i == "\\":
                next += "\\"
            else:
                next += "\\%s" % i
        else:
            raise Exception(state) # FIXME: be more specific
    if state == "some":
        result += [next]
    elif state != "none":
        raise Exception(state) # FIXME: be more specific
    return result

if __name__ == "__main__":
    user = None
    while True:
        if user is None:
            message = "\033[1;35m%s>\033[0m " % C.NAME
        else:
            message = "\033[1;33m%s@\033[0m " % user._name
        try:
            command = parse(scan(message))
            if len(command) < 1:
                pass
            elif command[0] in ["help", "?"]:
                out("Welcome to Neat, a club management tool.")
                out()
                out("Type 'help' or '?' to see this message. Type 'quit',")
                out("'exit', or send your platform's EOF signal to end")
                out("your session. Press ^C (Ctrl+C) to kill a command.")
                out()
                out("migrate         create an account; link it with TidyHQ")
                out("authenticate    log in to Neat with your club account")
                out()
                out("id              prints the list of groups you are in")
            elif command[0] in ["quit", "exit"]:
                break
            elif command[0] == "migrate":
                migrate_first_time = False
                try:
                    importlib.reload(migrate)
                except NameError:
                    migrate_first_time = True
                if migrate_first_time:
                    import migrate
            elif command[0] == "authenticate":
                pair = Password.ask(C.DOMAIN)
                try:
                    user = User.authenticate(*pair)
                except (AuthenticationError, LDAPPasswordIsMandatoryError):
                    out("authenticate: bad username or password")
            elif command[0] == "id":
                if user is not None:
                    entry = user.get()
                    print(
                        "user: %d <%s>"
                        % (entry.uidNumber.value, entry.cn.value)
                    )
                    query = "(member=%s)" % entry.entry_dn
                    for group in Directory().reader("group", query=query).search():
                        print(
                            "group: %d <%s>"
                            % (group.gidNumber.value, group.cn.value)
                        )
            else:
                out("%s: command not found" % command[0])
        except EOFError:
            out()
            break
        except KeyboardInterrupt:
            out("\033[0m\033[7m^C\033[0m")
        except Exception as e:
            kind, value, trace = sys.exc_info()
            traceback.print_exception(kind, value, trace) # None)
