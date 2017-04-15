"""
Helper functions.
"""
from datetime import datetime
import time

from appdirs import user_data_dir
from six import string_types
from tqdm import tqdm

from .const import UTCF

APP_NAME = "QuiltCli"
APP_AUTHOR = "QuiltData"
BASE_DIR = user_data_dir(APP_NAME, APP_AUTHOR)


class FileWithReadProgress(object):
    """
    Acts like a file with mode='rb', but displays a progress bar while the file is read.
    """
    def __init__(self, path_or_fd):
        if isinstance(path_or_fd, string_types):
            self._fd = open(path_or_fd, 'rb')
            self._need_to_close = True
        else:
            self._fd = path_or_fd
            self._need_to_close = False

        self._fd.seek(0, 2)
        size = self._fd.tell()
        self._fd.seek(0)

        self._progress = tqdm(
            total=size,
            unit='B',
            unit_scale=True
        )

    def read(self, size=-1):
        """Read bytes and update the progress bar."""
        buf = self._fd.read(size)
        self._progress.update(len(buf))
        return buf

    def tell(self):
        """Get the file position."""
        return self._fd.tell()

    def seek(self, offset, whence=0):
        """Set the new file position."""
        self._fd.seek(offset, whence)

    def close(self):
        """Close the file and the progress bar."""
        self._progress.close()
        if self._need_to_close:
            self._fd.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.close()


def file_to_str(fname):
    """
    Read a file into a string
    PRE: fname is a small file (to avoid hogging memory and its discontents)
    """
    data = None
    # rU = read with Universal line terminator
    with open(fname, 'rU') as f:
        data = f.read()
    return data


def make_comparator(func):
    """
    for use in sorting
    func: is a binary operator returning True/False
    """
    def compare(left, right):
        """
        apply func in one of three possible senses
        """
        if func(left, right):
            return -1
        elif func(right, left):
            return 1
        else:
            return 0
        return compare

def parse_utc(utc):
    """
    convert quilt server UTC strings into  datetime objects
    """
    return datetime.strptime(utc, UTCF)

# http://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime
def utc2local(utc):
    """
    convert utc time to local time; beware of stackoverflow magic :-/
    """
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)

    return utc + offset
