import botocore.auth
import os
import re

from datetime import timedelta


FAKETIME_REALTIME_FILE = os.environ.get('FAKETIME_REALTIME_FILE')


def real_time():
    with open(FAKETIME_REALTIME_FILE) as open_file:
        return float(open_file.read())


class PatchedDatetimeModule(object):
    """
    Wrapper for the datetime module that uses libfaketimefs's realtime file
    to determine the current time, rather than making a system call which
    would be intercepted by libfaketime.

    """

    def __init__(self, datetime):

        self._datetime = datetime

        class date(datetime.date):

            @classmethod
            def today(cls):
                t = real_time()
                return cls.fromtimestamp(t)

        class datetime(datetime.datetime):

            @classmethod
            def now(cls, tz=None):
                t = real_time()
                return cls.fromtimestamp(t, tz)

            @classmethod
            def utcnow(cls):
                t = real_time()
                return cls.utcfromtimestamp(t)

        self.date = date
        self.datetime = datetime

    def __getattr__(self, name):
        return getattr(self._datetime, name)


def patch_botocore():
    """
    Patches botocore to work while using libfaketime and libfaketimefs.

    """

    if FAKETIME_REALTIME_FILE:

        botocore.auth.datetime = PatchedDatetimeModule(
            datetime=botocore.auth.datetime,
        )

        # It looks like requests made using some older AWS signature versions
        # would require patching the following variables, but I'm not sure
        # how to test them so they haven't been patched.
        # * botocore.auth.formatdate for email.formatdate(usegmt=True)
        # * botocore.auth.time for time.gmtime() and time.time()
