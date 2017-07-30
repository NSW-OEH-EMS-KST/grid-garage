import datetime
import os
from collections import OrderedDict
from re import compile
import arcpy as ap
import collections
import csv
import numpy


# arc_data_types = "Any,Container,Geo,FeatureDataset,FeatureClass,PlanarGraph,GeometricNetwork,Topology,Text,Table,RelationshipClass,RasterDataset,RasterBand,TIN,CadDrawing,RasterCatalog,Toolbox,Tool,NetworkDataset,Terrain,RepresentationClass,CadastralFabric,SchematicDataset,Locator"
arc_data_types = "Any,CadDrawing,CadastralFabric,Container,FeatureClass,FeatureDataset,Geo,GeometricNetwork,LasDataset,Layer,Locator,Map,MosaicDataset,NetworkDataset,PlanarGraph,RasterCatalog,RasterDataset,RelationshipClass,RepresentationClass,Style,Table,Terrain,Text,Tin,Tool,Toolbox,Topology"
datatype_list = arc_data_types.split(",")

raster_formats = ["Esri Grid", "tif", "img"]
resample_methods = ["NEAREST", "BILINEAR", "CUBIC", "MAJORITY"]
aggregation_methods = ["SUM", "MEAN", "MAXIMUM", "MINIMUM", "MEDIAN"]
data_nodata = ["DATA", "NODATA"]
expand_trunc = ["EXPAND", "TRUNCATE"]
stats_type = ["ALL", "MEAN", "MAJORITY", "MAXIMUM", "MEDIAN", "MINIMUM", "RANGE", "STD", "SUM", "VARIETY"]
pixel_type = ["1_BIT", "2_BIT", "4_BIT", "8_BIT_UNSIGNED", "8_BIT_SIGNED", "16_BIT_UNSIGNED", "16_BIT_SIGNED", "32_BIT_UNSIGNED", "32_BIT_SIGNED", "32_BIT_FLOAT", "64_BIT"]
raster_formats2 = sorted(["tif", "img", "bmp", "gif", "png", "jpg", "jp2", "dat", "Esri Grid", "bil", "bsq", "bip"])
transform_methods = ["STANDARDISE", "STRETCH", "NORMALISE", "LOG", "SQUAREROOT", "INVERT"]


class DoesNotExistError(ValueError):
    def __init__(self, geodata):
        super(DoesNotExistError, self).__init__(self, "{} does not exist".format(geodata))


class NotRasterError(ValueError):
    def __init__(self, geodata, datatype):
        super(NotRasterError, self).__init__(self, "{} is not a raster dataset. Its data type is '{}'".format(geodata, datatype))


class NotVectorError(ValueError):
    def __init__(self, geodata, datatype):
        super(NotVectorError, self).__init__(self, "{} is not a vector dataset. Its data type is '{}'".format(geodata, datatype))


class NotTableError(ValueError):
    def __init__(self, geodata, datatype):
        super(NotTableError, self).__init__(self, "{} is not a table dataset. Its data type is '{}'".format(geodata, datatype))


class UnknownSrsError(ValueError):
    def __init__(self, geodata):
        super(UnknownSrsError, self).__init__(self, "Dataset '{}' has an unknown spatial reference system".format(geodata))


class UnknownDataTypeError(ValueError):
    def __init__(self, geodata, datatype):
        super(UnknownDataTypeError, self).__init__(self, "Dataset '{}' has an unknown data type".format(geodata, datatype))


class UnmatchedSrsError(ValueError):
    def __init__(self, srs1, srs2):
        super(UnmatchedSrsError, self).__init__(self, "Spatial references do not match '{}' != '{}'".format(srs1, srs2))


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


# @base.log.log
# def get_field_list(dataset, wild_card=None, field_type=None):
#
#     if not geodata_exists(dataset):
#         raise DoesNotExistError(dataset)
#
#     return ap.ListFields(dataset, wild_card, field_type)


# def table_conversion(in_rows, out_path, out_name):
#
#     """ Copy a file-based table to a local database, returns full path to new table if successful"""
#     fms = ap.FieldMappings()
#     fms.addTable(in_rows)
#
#     with open(in_rows) as csv_file:
#
#         reader = csv.DictReader(csv_file)
#
#     def get_max_string_length(field):
#
#         return max([len(d[field]) for d in reader])
#
#     sus_string_fields = [(f, i) for i, f in enumerate(fms.fields) if f.type == "String"]
#     fix_string_fields = [(f, i, get_max_string_length(f)) for f, i, x in sus_string_fields]
#     for f, i, mx in fix_string_fields:
#         fm = fms.getFieldMap(i)
#         fld = fm.outputField
#         fld.length = mx + 10
#         fm.outputField = fld
#         fms.replaceFieldMap(i, fm)
#
#     sus_single_fields = [i for i, f in enumerate(fms.fields) if f.type == "Single"]
#     for i in sus_single_fields:
#         fm = fms.getFieldMap(i)
#         fld = fm.outputField
#         fld.type = "Double"
#         fm.outputField = fld
#         fms.replaceFieldMap(i, fm)
#
#     ap.TableToTable_conversion(in_rows, out_path, out_name, None, fms, None)
#     ret = os.path.join(out_path, out_name)
#
#     return ret


def describe_arc(geodata):

    if not geodata_exists(geodata):
        raise DoesNotExistError(geodata)

    return ap.Describe(geodata)


def is_local_gdb(workspace):
    return describe_arc(workspace).workspaceType == "LocalDatabase"


def is_file_system(workspace):
    return describe_arc(workspace).workspaceType == "FileSystem"


def get_search_cursor_rows(in_table, field_names, where_clause=None):

    def _get_search_cursor(in_table_sc, field_names_sc, where_clause_sc=where_clause, spatial_reference=None, explode_to_points=None, sql_clause=None):

        return ap.da.SearchCursor(in_table_sc, field_names_sc, where_clause_sc, spatial_reference, explode_to_points, sql_clause)

    # get a search cursor, listify it, release it
    sc = _get_search_cursor(in_table, field_names, where_clause_sc=where_clause)
    rows = [row for row in sc]
    del sc

    return rows


def geodata_exists(geodata):
    if geodata:
        return ap.Exists(geodata)
    else:
        return False


def make_tuple(ob):
    return ob if isinstance(ob, (list, tuple)) else [ob]


def split_up_filename(filename):
    """ Return strings representing the parts of the filename.

    Parameters:
        filename (string) = The filename string to be parsed
    Output:
        returns 4 strings: path, base (=name+ext), name, ext for the filename
    """
    the_path, basename = os.path.split(filename)
    name, ext = os.path.splitext(basename)
    return the_path, basename, name, ext


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
            val = datetime.datetime.strptime(match, '%Y%m%d')
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

# @base.log.log_error
def parse_proj_string_for_name(proj_string):
    # s = PROJCS['GDA_1994_Australia_Albers', GEOGCS[
    #     'GCS_GDA_1994', DATUM['D_GDA_1994', SPHEROID['GRS_1980', 6378137.0, 298.257222101]], PRIMEM['Greenwich', 0.0],
    #     UNIT['Degree', 0.0174532925199433]], PROJECTION['Albers'], PARAMETER['False_Easting', 0.0], PARAMETER[
    #            'False_Northing', 0.0], PARAMETER['Central_Meridian', 132.0], PARAMETER['Standard_Parallel_1', -18.0],
    #        PARAMETER['Standard_Parallel_2', -36.0], PARAMETER['Latitude_Of_Origin', 0.0], UNIT['Meter', 1.0]]
    x, y, z = proj_string.split("[", 2)
    return y.split(",")[0].strip("'")


# @base.log.log_error
def make_raster_name(like_name, out_wspace, ext='', prefix='', suffix=''):
    _, __, r_name, r_ext = split_up_filename(like_name)

    ext = "" if (is_local_gdb(out_wspace) or ext == "Esri Grid") else ext
    ext = "." + ext if (ext and ext[0] != ".") else ext

    raster_name = ap.ValidateTableName(prefix + r_name + suffix, out_wspace)
    raster_name = ap.CreateUniqueName(raster_name, out_wspace)

    return os.path.join(out_wspace, raster_name + ext)


# @base.log.log_error
def make_table_name(like_name, out_wspace, ext='', prefix='', suffix=''):
    _, __, t_name, t_ext = split_up_filename(like_name)

    ext = "" if (is_local_gdb(out_wspace) or ext == "Esri Grid") else ext
    ext = "." + ext if (ext and ext[0] != ".") else ext

    table_name = ap.ValidateTableName(prefix + t_name + suffix, out_wspace)
    table_name = ap.CreateUniqueName(table_name, out_wspace)

    return os.path.join(out_wspace, table_name + ext)


# @base.log.log_error
def make_vector_name(like_name, out_wspace, ext='', prefix='', suffix=''):
    _, __, v_name, v_ext = split_up_filename(like_name)

    ext = "" if is_local_gdb(out_wspace) else ext
    ext = "." + ext if (ext and ext[0] != ".") else ext

    vector_name = ap.ValidateTableName(prefix + v_name + suffix, out_wspace)
    vector_name = ap.CreateUniqueName(vector_name, out_wspace)

    return os.path.join(out_wspace, vector_name + ext)


# @base.log.log_error
def is_table(item):
    if not geodata_exists(item):
        raise DoesNotExistError(item)

    d = ap.Describe(item)
    try:
        return d.dataType in ["Table"]
    except:
        return False


# @base.log.log_error
def is_vector(item):
    if not geodata_exists(item):
        raise DoesNotExistError(item)

    d = ap.Describe(item)
    try:
        return d.dataType in ["FeatureClass", "ShapeFile"]
    except:
        return False


# @base.log.log_error
def is_raster(item):
    if not geodata_exists(item):
        raise DoesNotExistError(item)

    d = ap.Describe(item)
    try:
        return d.dataType == "RasterDataset"
    except:
        return False


# @base.log.log_error
def walk(workspace, data_types=None, types=None, followlinks=True):
    x = []
    for root, dirs, files in ap.da.Walk(workspace, datatype=data_types, type=types, followlinks=followlinks):
        for f in files:
            x.append(os.path.join(root, f))
    return x


# @base.log.log_error
def describe(geodata):

    describe_field_groups = dict(
        general=["baseName", "catalogPath", "children", "childrenExpanded", "dataElementType", "dataType", "extension", "file", "fullPropsRetrieved", "metadataRetrieved", "name", "path"],
        file=["FileSizeKB", "FileModified"],
        dataset=["canVersion", "datasetType", "DSID", "extent", "isVersioned", "MExtent", "spatialReference", "ZExtent"],
        table=["hasOID", "OIDFieldName", "fields", "indexes"],
        raster=["bandCount", "compressionType", "format", "permanent", "sensorType"],
        raster_band=["height", "isInteger", "meanCellHeight", "meanCellWidth", "noDataValue", "pixelType", "primaryField", "tableType", "width"],
        raster_band_stats=["MINIMUM", "MAXIMUM", "MEAN", "STD", "UNIQUEVALUECOUNT", "TOP", "LEFT", "RIGHT", "BOTTOM", "CELLSIZEX", "CELLSIZEY", "VALUETYPE", "COLUMNCOUNT", "ROWCOUNT", "BANDCOUNT", "ANYNODATA", "ALLNODATA", "SENSORNAME", "PRODUCTNAME", "ACQUSITIONDATE", "SOURCETYPE", "SUNELEVATION", "CLOUDCOVER", "SUNAZIMUTH", "SENSORAZIMUTH", "SENSORELEVATION", "OFFNADIR", "WAVELENGTH"])

    d = ap.Describe(geodata)
    result = {}
    for group, attributes in describe_field_groups.iteritems():
        group_atts = {"{0}_{1}".format(group, att): getattr(d, att, None) for att in attributes}
        result.update(group_atts)

    # check for table fields which need to be stringified
    fs = result.get("table_fields", None)
    fs = fs if fs else []  # in case above returns a value of none, can't combine these lines
    fs = [str(f.name) for f in fs]
    fs = ", ".join(fs)
    result["table_fields"] = fs

    # check for table indexes which need to be stringified
    xs = result.get("table_indexes", [])
    xs = xs if xs else []  # in case above returns a value of none, can't combine these lines
    xs = [x.name for x in xs]
    xs = ", ".join(xs)
    result["table_indexes"] = xs

    # check for child datasets which need to be stringified
    cs = result.get("general_children", [])
    cs = [c.name for c in cs]
    cs = ", ".join(cs)
    result["general_children"] = cs

    # check for spatial reference which needs to be stringified
    sr = result.get("dataset_spatialReference", None)
    if sr:
        result["dataset_spatialReference"] = sr.name

    # # check for raster bands which need to be looked at
    # dt = result.get("dataset_datasetType", None)
    # if dt == "RasterDataset" and cs:
    #     cs = cs.split(", ")
    #     for c in cs:
    #         bnd = join_up_filename(geodata, c)
    #         d = ap.Describe(bnd)
    #         ns = ["raster_band_{0}".format(a) for a in describe_field_groups["raster_band"]]
    #         for n in ns:
    #             a = getattr(d, n, "")
    #             result[n] += ", {0}".format(a)
            #     group_atts = {"{0}_{1}".format(group, att): getattr(d, att, None) for att in attributes}
            #     result.update(group_atts)
            # bp = geta(tool.describe(bnd), fields_band)
            # for field in fields_band_ex:

        # result["dataset_spatialReference"] = sr.name

    # return an ordered dictionary
    od = collections.OrderedDict()
    od["geodata"] = geodata
    for i, attributes in sorted(result.items()):
        od[i] = attributes

    return od
    # # band properties
    # if do_band:
    #     children = getattr(desc, 'children', None)
    #     getr = tool.get_raster_property
    #     i = 0
    #     for child in children:
    #         cname = child.name
    #         i += 1
    #         bnd = tool.join_up(raster, cname)
    #         bp = geta(tool.describe(bnd), fields_band)
    #         for field in fields_band_ex:
    #             z = getr(raster, field, cname, as_string=True)
    #             bp.update(z)
    #         update({"Band_{0}".format(i): bp})


# @base.log.log_error
def get_transformation(in_ds, out_cs, overrides=None):

    cs_in = get_srs(in_ds, raise_unknown_error=True, as_object=True)
    # def parse_proj_string_for_name(proj_string):
    #     # s = PROJCS['GDA_1994_Australia_Albers', GEOGCS[
    #     #     'GCS_GDA_1994', DATUM['D_GDA_1994', SPHEROID['GRS_1980', 6378137.0, 298.257222101]], PRIMEM['Greenwich', 0.0],
    #     #     UNIT['Degree', 0.0174532925199433]], PROJECTION['Albers'], PARAMETER['False_Easting', 0.0], PARAMETER[
    #     #            'False_Northing', 0.0], PARAMETER['Central_Meridian', 132.0], PARAMETER['Standard_Parallel_1', -18.0],
    #     #        PARAMETER['Standard_Parallel_2', -36.0], PARAMETER['Latitude_Of_Origin', 0.0], UNIT['Meter', 1.0]]
    #     x, y = proj_string.split("[", 1)
    #     return y.split(",")[0].strip("'")

    if cs_in.GCS.name == out_cs.GCS.name:  # the same datum, no tx required
        return "#"

    # if cs_in.GCS.datumCode != cs_out.GCS.datumCode:
    try:
        lst = ap.ListTransformations(cs_in, out_cs)
    except Exception as e:
        e = ValueError("cs_in= " + cs_in + " out_cs= " + out_cs + " e: " + str(e))
        # base.log.debug("Raising {}".format(e))
        raise e
    if lst:
        shortest = min(lst, key=len)
    else:
        e = ValueError("Datum transformation was not found for {0} (1) -> {2}".format(in_ds, cs_in, out_cs))
        # base.log.debug("Raising {}".format(e))
        raise e

    if overrides:
        ov = overrides.get(shortest, None)
        if ov:
            shortest = ov

    return shortest
    # # get transformation
    # shortest = ()
    # cs_in = Describe(r_in).spatialReference
    # # cs_in = ap.CreateSpatialReference_management(spatial_reference_template=r_in).re
    # self.send_info(cs_in.GCS.datumCode)
    # self.send_info(self.out_cs.GCS.datumCode)
    # if cs_in.GCS.datumCode != self.out_cs.GCS.datumCode:
    #     lst = ap.ListTransformations(cs_in, self.out_cs)
    #     shortest = min(lst, key=len) if lst else ()
    #     if not shortest:
    #         raise ValueError("Datum transformation was not found for {0} -> {1}".format(cs_in.name, self.out_cs))
    #     ov = self.overrides.get(shortest, None)
    #     if ov:
    #         shortest = ov


def get_srs(geodata, raise_unknown_error=False, as_object=False):

    if not geodata_exists(geodata):

        raise DoesNotExistError(geodata)

    try:
        srs = ap.Describe(geodata).spatialReference
    except:
        raise ValueError("'{}' has no 'spatialReference' property".format(geodata))

    if "unknown" in srs.name.lower() and raise_unknown_error:

        raise UnknownSrsError(geodata)

    if as_object:
        return srs
    else:
        return srs.name


def validate_geodata(geodata, raster=False, vector=False, table=False, srs_known=False, message_func=None):

    if message_func:
        message_func("Validating '{}'".format(geodata))

    if not geodata_exists(geodata):

        raise DoesNotExistError(geodata)

    try:
        dt = ap.Describe(geodata).dataType
    except:
        raise UnknownDataTypeError(geodata, "No datatype property")

    if raster and dt not in ["RasterDataset"]:

        raise NotRasterError(geodata, dt)

    if vector and dt not in ["FeatureClass", "ShapeFile"]:

        raise NotVectorError(geodata, dt)

    if table and dt not in ["Table", "TableView"]:

        raise NotTableError(geodata, dt)

    if srs_known:

        get_srs(geodata, raise_unknown_error=True)

    return


def compare_srs(srs1, srs2, raise_no_match_error=False, other_condition=True):

    return_value = False

    if not other_condition:

        return_value = False

    elif srs1 == srs2:

        return_value = True

    else:
        if raise_no_match_error:

            raise UnmatchedSrsError(srs1, srs2)

    return return_value


# @base.log.log_error
def get_band_nodata_value(raster, bandindex=1):

    d = ap.Describe(os.path.join(raster, "Band_{}".format(bandindex)))
    try:
        ndv = d.noDataValue
    except:
        ndv = "#"

    # base.log.debug("ndv={}".format(ndv))

    return ndv


