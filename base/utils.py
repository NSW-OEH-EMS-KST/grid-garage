# import arcpy
import datetime
import os


def make_tuple(ob):
    return ob if isinstance(ob, (list, tuple)) else [ob]


def split_up_filename(filename):
    """ Return strings representing the parts of the filename.

    Parameters:
        filename (string) = The filename string to be parsed
    Output:
        returns 4 strings: path, base (=name+ext), name, ext for the filename
    """
    pth, base = os.path.split(filename)
    name, ext = os.path.splitext(base)
    return pth, base, name, ext


def time_stamp(fmt='%Y%m%d_%H%M%S'):
    """ Return a current time stamp.

    Parameters:
        fmt (string) = Format string for the output
    Output:
        returns a string unless the default 'fmt' argument is empty ('')
    """
    return datetime.datetime.now().strftime(fmt)


def join_up_filename(workspace, filename, ext=''):
    """ Joins file elements into a full path and name.

    Parameters:
        workspace (string) = The name of the workspace
        filename (string) = The name of the file with or without extension
        ext (string) = The extension if not included in filename
    Output:
        returns a string representing a full path (may or may not exist)
    """
    if ext and ext[0] != '.':
        ext += '.'

    return os.path.join(workspace, filename) + ext
