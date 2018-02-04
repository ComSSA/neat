import requests

import neat
from configuration import C
from tidy import Club
from user import User
from password import Password
from directory import Directory, AuthenticationError

T = Club(C.TIDY_NAME, C.TIDY_CLIENT, C.TIDY_SECRET)
T_pair = None
while T._token is None:
    try:
        T_pair = Password.ask("TidyHQ", T_pair)
        T.authenticate(*T_pair)
    except requests.exceptions.HTTPError:
        pass
print()
me = T.me()
T_prefix = "TidyHQ contact #%d" % me._data["id"]
membership = me.membership()
if membership is None:
    print(
        "%s: you are not an active member"
        % (T_prefix)
    )
else:
    print(
        "%s: you are an active member until %s"
        % (T_prefix, membership["end_date"])
    )
    username = me.username()
    forward_linking_is_required = False
    if username is None:
        forward_linking_is_required = True
        print(
            "%s: not associated with a club account"
            % (T_prefix)
        )
        reserved_usernames = C.RESERVED_USERNAMES
        print()
        print(
            "Please choose a new username for %s, or if you think you have"
            % (C.DOMAIN)
        )
        print(
            "one, enter it below, but do not write the %s. Usernames must"
            % (C.DOMAIN)
        )
        print(
            "not be less than 3 characters, not be more than 8 characters,"
        )
        print(
            "start with [a-z], contain only [a-z0-9], and not be reserved:"
        )
        print()
        reserved_usernames_line_length = 0
        for i in reserved_usernames:
            reserved_usernames_line_length += len(i) + 1
            if reserved_usernames_line_length > 70:
                reserved_usernames_line_length = 0
                print()
            print(i, end=" ")
        print()
        print()
        username = User.new(C.DOMAIN, reserved_usernames)
    else:
        print(
            "%s: associated with %s@%s"
            % (T_prefix, username, C.DOMAIN)
        )
    if username is not None:
        reverse_linking_is_required = False
        l_prefix = (
            "%s@%s"
            % (username, C.DOMAIN)
        )
        try:
            user = User(username).get()
            if user.neatTidyContactNumber.value is None:
                reverse_linking_is_required = True
                print(
                    "%s: not associated with a TidyHQ contact"
                    % (l_prefix)
                )
            else:
                print(
                    "%s: associated with TidyHQ contact #%d"
                    % (l_prefix, user.neatTidyContactNumber.value)
                )
                if me._data["id"] != user.neatTidyContactNumber.value:
                    reverse_linking_is_required = True
                    print(
                        "%s: TidyHQ contact #%d belongs to %s"
                        % (
                            l_prefix,
                            user.neatTidyContactNumber.value,
                            TidyHQ.Contact(
                                t, user.neatTidyContactNumber.value
                            )._data["email_address"]
                        )
                    )
        except IndexError:
            print(
                "%s: creating a new account"
                % (l_prefix)
            )
            print()
            print(
                "Now it's time to choose a password. Please choose a password"
            )
            print(
                "that's no less than 10 characters, but no more than 72."
            )
            print()
            print(
                "Passwords are hashed with OpenBSD's bcrypt algorithm, but"
            )
            print(
                "*please* choose a good password. If you're a committee member,"
            )
            print(
                "your account has access to all of our passwords and can root"
            )
            print(
                "all of our servers, so I'm really serious about this."
            )
            print()
            User(username).create(
                Password.new(username),
                input("\nThe email address you prefer to use: "),
                input("The name you prefer to be called by: "),
                me._data["first_name"], me._data["last_name"], me._data["id"]
            )
            print()
            print(
                "%s: created account"
                % (l_prefix)
            )
        if reverse_linking_is_required:
            print()
            print(
                "To link %s@%s back to TidyHQ contact #%d,"
                % (user.uid, C.DOMAIN, me._data["id"])
            )
            print(
                "please log in:"
            )
            print()
            user_test = None
            neat_password = None
            while user_test is None:
                neat_password = Password.ask(C.DOMAIN, neat_password, user.uid)
                try:
                    user_test = Directory(user.entry_dn, neat_password[1])
                except AuthenticationError:
                    pass
            user = User(user.uid.value).get()
            user.neatTidyContactNumber = me._data["id"]
            user.entry_commit_changes()
        if forward_linking_is_required:
            me.username(username)
neat.out("\nNow try the 'authenticate' command!")
