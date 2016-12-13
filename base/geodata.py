import arcpy
import os
import collections
import csv
from base.utils import split_up_filename

# arc_data_types = "Any,Container,Geo,FeatureDataset,FeatureClass,PlanarGraph,GeometricNetwork,Topology,Text,Table,RelationshipClass,RasterDataset,RasterBand,TIN,CadDrawing,RasterCatalog,Toolbox,Tool,NetworkDataset,Terrain,RepresentationClass,CadastralFabric,SchematicDataset,Locator"
arc_data_types = "Any,CadDrawing,CadastralFabric,Container,FeatureClass,FeatureDataset,Geo,GeometricNetwork,LasDataset,Layer,Locator,Map,MosaicDataset,NetworkDataset,PlanarGraph,RasterCatalog,RasterDataset,RelationshipClass,RepresentationClass,Style,Table,Terrain,Text,Tin,Tool,Toolbox,Topology"
datatype_list = arc_data_types.split(",")

raster_formats = ["Esri Grid", "tif", "img"]
resample_methods = ["NEAREST", "BILINEAR", "CUBIC", "MAJORITY"]
aggregation_methods = ["SUM", "MEAN", "MAXIMUM", "MINIMUM", "MEDIAN"]
data_nodata = ["DATA", "NODATA"]
expand_trunc = ["EXPAND", "TRUNCATE"]
stats_type = ["MEAN", "MAJORITY", "MAXIMUM", "MEDIAN", "MINIMUM", "RANGE", "STD", "SUM", "VARIETY"]
pixel_type = ["1_BIT", "2_BIT", "4_BIT", "8_BIT_UNSIGNED", "8_BIT_SIGNED", "16_BIT_UNSIGNED", "16_BIT_SIGNED", "32_BIT_UNSIGNED", "32_BIT_SIGNED", "32_BIT_FLOAT", "64_BIT"]
raster_formats2 = ["TIFF", "IMAGINE Image", "BMP", "GIF", "PNG", "JPEG", "JPEG2000", "DTED", "Esri Grid","Esri BIL", "Esri BSQ", "Esri BIP", "ENVI,CRF", "MRF"]
transform_methods = ["STANDARDISE", "STRETCH", "NORMALISE", "LOG", "SQUAREROOT", "INVERT"]


class DoesNotExistError(ValueError):
    def __init__(self, geodata):
        super(DoesNotExistError, self).__init__("{0} does not exist".format(geodata))


class NotRasterError(ValueError):
    def __init__(self, geodata):
        super(NotRasterError, self).__init__("{0} is not a raster dataset".format(geodata))


class NotVectorError(ValueError):
    def __init__(self, geodata):
        super(NotVectorError, self).__init__("{0} is not a vector dataset".format(geodata))


class UnknownSrsError(ValueError):
    def __init__(self, geodata):
        super(UnknownSrsError, self).__init__("Dataset '{0}' has an unknown spatial reference system".format(geodata))


class UnmatchedSrsError(ValueError):
    def __init__(self, srs1, srs2):
        super(UnmatchedSrsError, self).__init__("Spatial references do not match '{0}' != '{1}'".format(srs1, srs2))


# these few functions are not made methods so that back-end modules can import them easily for use

def table_conversion(in_rows, out_path, out_name):
    """ Copy a file-based table to a local database, returns full path to new table if successful"""
    fms = arcpy.FieldMappings()
    fms.addTable(in_rows)

    # make a list of fields we will look at for size suitability
    sus_fields, i = [], -1
    for f in fms.fields:
        i += 1
        if f.type == "String":  # and f.length == 255:
            sus_fields.append([f.name, i])  # need the index later on...

    # now we will run through the rows and see if we have issues
    failed = ""
    try:
        failed = "on opening file {0}".format(in_rows)
        with open(in_rows) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:  # each row is a dict of results
                failed = "on using row {0}".format(row)
                for f, j in sus_fields:
                    ln = len(row[f])
                    fm = fms.getFieldMap(j)
                    fld = fm.outputField
                    if ln > fld.length:
                        fld.length = ln + 10
                        fm.outputField = fld
                        fms.replaceFieldMap(j, fm)

    except Exception as e:
        arcpy.AddWarning("'{0}' validation failed: {1} {2}".format(in_rows, failed, str(e)))

    try:
        # TableToTable_conversion (in_rows, out_path, out_name, {where_clause}, {field_mapping}, {config_keyword})
        arcpy.TableToTable_conversion(in_rows, out_path, out_name, None, fms, None)
        return os.path.join(out_path, out_name)

    except Exception as e:
        arcpy.AddWarning(e.message)
        return None


def describe_arc(geodata):

    if not geodata_exists(geodata):
        raise DoesNotExistError(geodata)

    return arcpy.Describe(geodata)


def is_local_gdb(workspace):
    return describe_arc(workspace).workspaceType == "LocalDatabase"


def is_file_system(workspace):
    return describe_arc(workspace).workspaceType == "FileSystem"


def get_search_cursor_rows(in_table, field_names, where_clause=None):

    def _get_search_cursor(in_table_sc, field_names_sc, where_clause_sc=where_clause, spatial_reference=None, explode_to_points=None, sql_clause=None):
        return arcpy.da.SearchCursor(in_table_sc, field_names_sc, where_clause_sc, spatial_reference, explode_to_points, sql_clause)

    # get a search cursor, listify it, release it
    sc = _get_search_cursor(in_table, field_names, where_clause_sc=where_clause)
    rows = [row for row in sc]
    del sc

    return rows


def geodata_exists(geodata):
    if geodata:
        return arcpy.Exists(geodata)
    else:
        return False


# the main class that is attributed to the tool as 'geodata'
class GeodataUtils(object):
    def __init__(self):
        self.table_conversion = table_conversion
        self.describe_arc = describe_arc
        self.is_local_gdb = is_local_gdb
        self.get_search_cursor_rows = get_search_cursor_rows
        self.datatype_list = datatype_list
        self.exists = geodata_exists
        self.rename = arcpy.Rename_management
        self.copy_geodata = arcpy.Copy_management
        self.copy_feature = arcpy.CopyFeatures_management
        self.delete = arcpy.Delete_management
        self.clip = arcpy.Clip_analysis
        return

    @staticmethod
    def make_raster_name(like_name, out_wspace, ext='', suffix=''):
        _, __, r_name, r_ext = split_up_filename(like_name)

        ext = "" if is_local_gdb(out_wspace) or ext == "Esri Grid" else ext
        ext = "." + ext if (ext and ext[0] != ".") else ext

        raster_name = arcpy.ValidateTableName(r_name + suffix, out_wspace)
        raster_name_full = os.path.join(out_wspace, raster_name)

        if arcpy.Exists(raster_name_full):
            raster_name = arcpy.CreateUniqueName(raster_name, out_wspace)

        return os.path.join(out_wspace, raster_name + ext)

    @staticmethod
    def make_table_name(like_name, out_wspace, ext=''):
        _, __, gd_name, gd_ext = split_up_filename(like_name)

        ext = "" if is_local_gdb(out_wspace) else ext
        ext = "." + ext if (ext and ext[0] != ".") else ext

        table_name = os.path.join(out_wspace, gd_name + ext)
        if arcpy.Exists(table_name):
            table_name = arcpy.CreateUniqueName(gd_name, out_wspace)
        else:
            table_name = arcpy.ValidateTableName(gd_name, out_wspace)

        return os.path.join(out_wspace, table_name + ext)

    @staticmethod
    def make_vector_name(like_name, out_wspace, ext=''):
        _, __, gd_name, gd_ext = split_up_filename(like_name)

        ext = "" if is_local_gdb(out_wspace) else ext
        ext = "." + ext if (ext and ext[0] != ".") else ext

        table_name = os.path.join(out_wspace, gd_name + ext)
        if arcpy.Exists(table_name):
            table_name = arcpy.CreateUniqueName(gd_name, out_wspace)
        else:
            table_name = arcpy.ValidateTableName(gd_name, out_wspace)

        return os.path.join(out_wspace, table_name + ext)

    @staticmethod
    def is_vector(item):
        if not geodata_exists(item):
            raise DoesNotExistError(item)

        d = arcpy.Describe(item)
        try:
            return d.dataType in ["FeatureClass", "ShapeFile"]
        except:
            return False

    @staticmethod
    def is_raster(item):
        if not geodata_exists(item):
            raise DoesNotExistError(item)

        d = arcpy.Describe(item)
        try:
            return d.dataType == "RasterDataset"
        except:
            return False

    @staticmethod
    def walk(workspace, data_types=None, types=None, followlinks=True):
        x = []
        for root, dirs, files in arcpy.da.Walk(workspace, datatype=data_types, type=types, followlinks=followlinks):
            for f in files:
                x.append(os.path.join(root, f))
        return x

    @staticmethod
    def describe(geodata):

        describe_field_groups = dict(
            general=["baseName", "catalogPath", "children", "childrenExpanded", "dataElementType", "dataType", "extension", "file", "fullPropsRetrieved", "metadataRetrieved", "name", "path"],
            file=["FileSizeKB", "FileModified"],
            dataset=["canVersion", "datasetType", "DSID", "extent", "isVersioned", "MExtent", "spatialReference", "ZExtent"],
            table=["hasOID", "OIDFieldName", "fields", "indexes"],
            raster=["bandCount", "compressionType", "format", "permanent", "sensorType"],
            raster_band=["height", "isInteger", "meanCellHeight", "meanCellWidth", "noDataValue", "pixelType", "primaryField", "tableType", "width"],
            raster_band_stats=["MINIMUM", "MAXIMUM", "MEAN", "STD", "UNIQUEVALUECOUNT", "TOP", "LEFT", "RIGHT", "BOTTOM", "CELLSIZEX", "CELLSIZEY", "VALUETYPE", "COLUMNCOUNT", "ROWCOUNT", "BANDCOUNT", "ANYNODATA", "ALLNODATA", "SENSORNAME", "PRODUCTNAME", "ACQUSITIONDATE", "SOURCETYPE", "SUNELEVATION", "CLOUDCOVER", "SUNAZIMUTH", "SENSORAZIMUTH", "SENSORELEVATION", "OFFNADIR", "WAVELENGTH"])

        d = arcpy.Describe(geodata)
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
        #         bnd = utils.join_up(geodata, c)
        #         d = arcpy.Describe(bnd)
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

    # @staticmethod
    def get_transformation(self, in_ds, out_cs, overrides=None):

        cs_in = self.get_srs(in_ds, raise_unknown_error=True, as_object=True)
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
            lst = arcpy.ListTransformations(cs_in, out_cs)
        except Exception as e:
            raise ValueError("cs_in= " + cs_in + " out_cs= " + out_cs + " e: " + str(e))
        if lst:
            shortest = min(lst, key=len)
        else:
            raise ValueError("Datum transformation was not found for {0} (1) -> {2}".format(in_ds, cs_in, out_cs))

        if overrides:
            ov = overrides.get(shortest, None)
            if ov:
                shortest = ov

        return shortest
        # # get transformation
        # shortest = ()
        # cs_in = Describe(r_in).spatialReference
        # # cs_in = arcpy.CreateSpatialReference_management(spatial_reference_template=r_in).re
        # self.send_info(cs_in.GCS.datumCode)
        # self.send_info(self.out_cs.GCS.datumCode)
        # if cs_in.GCS.datumCode != self.out_cs.GCS.datumCode:
        #     lst = arcpy.ListTransformations(cs_in, self.out_cs)
        #     shortest = min(lst, key=len) if lst else ()
        #     if not shortest:
        #         raise ValueError("Datum transformation was not found for {0} -> {1}".format(cs_in.name, self.out_cs))
        #     ov = self.overrides.get(shortest, None)
        #     if ov:
        #         shortest = ov

    def get_srs(self, geodata, raise_unknown_error=False, as_object=False):
        srs = arcpy.Describe(geodata).spatialReference

        if "unknown" in srs.name.lower() and raise_unknown_error:
            raise UnknownSrsError

        if as_object:
            return srs

        return srs.name

    def validate_geodata(self, geodata, raster=False, vector=False, srs_known=False):
        if not geodata_exists(geodata):
            raise DoesNotExistError(geodata)
        if raster and not self.is_raster(geodata):
            raise NotRasterError(geodata)
        if vector and not self.is_vector(geodata):
            raise NotVectorError(geodata)
        if srs_known:
            self.get_srs(geodata, raise_unknown_error=True)

    def compare_srs(self, srs1, srs2, raise_no_match_error=False, other_condition=True):
        if not other_condition:
            return False
        if srs1 == srs2:
            return True
        if raise_no_match_error:
                raise UnmatchedSrsError(srs1, srs2)



