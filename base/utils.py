import datetime
import os
from collections import OrderedDict
from re import compile


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


def get_ordered_dict_from_keys(key_seq, initial_val):
    return OrderedDict.fromkeys(sorted(key_seq), initial_val)


def decorate_func(var_name, var_value):
    """ Function decorator.

    Parameters:
        var_name = attribute name
        var_value = attribute var_value
    Output:
        returns a tuple of strings representing dates found
    """

    def decorated(func):
        setattr(func, var_name, var_value)
        return func

    return decorated


@decorate_func("pattern", None)
def find_date(s):
    """ Attempt to extract valid dates from a string.

    Parameters:
        s (string) = The string to be parsed for dates
    Output:
        returns a tuple of strings representing dates found
    """
    date_set = []

    if find_date.pattern is None:
        find_date.pattern = compile(r'\d{8}')

    for match in find_date.pattern.findall(s):
        try:
            val = datetime.strptime(match, '%Y%m%d')
            val = val.strftime('%Y/%m/%d')
            date_set.append(val)
        except ValueError:
            pass  # ignore, not date

    x = len(date_set)
    if x > 1:
        return date_set[0], date_set[1:]
    elif x == 1:
        return [date_set[0], None]
    else:
        return [None, None]


# def parse_proj_string_for_gcs(proj_string):
#     # s = PROJCS['GDA_1994_Australia_Albers', GEOGCS[
#     #     'GCS_GDA_1994', DATUM['D_GDA_1994', SPHEROID['GRS_1980', 6378137.0, 298.257222101]], PRIMEM['Greenwich', 0.0],
#     #     UNIT['Degree', 0.0174532925199433]], PROJECTION['Albers'], PARAMETER['False_Easting', 0.0], PARAMETER[
#     #            'False_Northing', 0.0], PARAMETER['Central_Meridian', 132.0], PARAMETER['Standard_Parallel_1', -18.0],
#     #        PARAMETER['Standard_Parallel_2', -36.0], PARAMETER['Latitude_Of_Origin', 0.0], UNIT['Meter', 1.0]]
#     x, y, z = proj_string.split("[", 2)
#     return y.split(",")[0].strip("'")

def parse_proj_string_for_name(proj_string):
    # s = PROJCS['GDA_1994_Australia_Albers', GEOGCS[
    #     'GCS_GDA_1994', DATUM['D_GDA_1994', SPHEROID['GRS_1980', 6378137.0, 298.257222101]], PRIMEM['Greenwich', 0.0],
    #     UNIT['Degree', 0.0174532925199433]], PROJECTION['Albers'], PARAMETER['False_Easting', 0.0], PARAMETER[
    #            'False_Northing', 0.0], PARAMETER['Central_Meridian', 132.0], PARAMETER['Standard_Parallel_1', -18.0],
    #        PARAMETER['Standard_Parallel_2', -36.0], PARAMETER['Latitude_Of_Origin', 0.0], UNIT['Meter', 1.0]]
    x, y, z = proj_string.split("[", 2)
    return y.split(",")[0].strip("'")

