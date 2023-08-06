from datetime import datetime, date
import json
import sys
import os
import sh
import contextlib


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def dump(obj):
    print('DUMP: {}'.format(json.dumps(obj, indent=1, default=json_serial)))


@contextlib.contextmanager
def safe_cd(path):
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)


# Exr shell overriden methods

def print_out(line):
    sys.stdout.write(line)
    sys.stdout.write("\n")
    sys.stdout.flush()


def print_err(line):
    sys.stderr.write(line)
    sys.stderr.write("\n")
    sys.stderr.flush()


nsh = None
if os.environ.get('TRAVIS', 'false') == 'true':
    nsh = sh(_out=sys.stdout, _err_to_out=True)
else:
    nsh = sh(_out=sys.stdout, _err_to_out=True, _tty_in=True)
