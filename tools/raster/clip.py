from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats
from arcpy import Clip_management
from base.utils import get_srs, validate_geodata, compare_srs, make_raster_name

tool_settings = {"label": "Clip",
                 "description": "Clips raster datasets",
                 "can_run_background": "True",
                 "category": "Raster"}

""" MAINTAIN_EXTENT - Adjust the number of columns and rows, then resample pixels so as to exactly match the clipping extent specified.
    NO_MAINTAIN_EXTENT - Maintain the cell alignment as the input raster and adjust the output extent accordingly."""

@results
class ClipRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.polygon_srs = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("rectangle", "Rectangle", "GPExtent", "Required", False, "Input", None, "extent", None, None)
    @parameter("polygons", "Polygon feature(s) to clip by", "GPFeatureLayer", "Optional", False, "Input", ["Polygon"], None, None, None)
    @parameter("clipping_geometry", "Use features for clipping", "GPBoolean", "Optional", False, "Input", None, None, None, None)
    @parameter("no_data_val", "Value for 'NoData'", "GPString", "Required", False, "Input", None, "nodata", None, None)
    @parameter("maintain_extent", "Maintain clipping extent", "GPString", "Optional", False, "Input", ["MAINTAIN_EXTENT", "NO_MAINTAIN_EXTENT"], None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        self.log.debug("IN self.parameter_strings= {}".format(self.parameter_strings))

        self.polygon_srs = get_srs(self.polygons, raise_unknown_error=True) if self.polygons != "#" else None
        self.clipping_geometry = "ClippingGeometry" if self.clipping_geometry != "#" else "NONE"

        self.log.debug("OUT")
        return

    def iterate(self):
        self.iterate_function_on_tableview(self.clip, "raster_table", ["raster"])
        return

    def clip(self, data):
        self.log.debug("IN data= {}".format(data))

        ras = data["raster"]
        validate_geodata(ras, raster=True)
        ras_srs = get_srs(ras, raise_unknown_error=True)
        self.log.debug("raster srs = {}".format(ras_srs))
        if self.polygons != "#":
            compare_srs(ras_srs, self.polygon_srs, raise_no_match_error=True, other_condition=(self.clipping_geometry != "NONE"))

        ras_out = make_raster_name(ras, self.results.output_workspace, self.raster_format, self.output_filename_prefix, self. output_filename_suffix)
        self.log.info("Clipping {0} -->> {1} ...".format(ras, ras_out))
        Clip_management(ras, self.rectangle, ras_out, self.polygons, self.no_data_val, self.clipping_geometry, self.maintain_extent)

        self.log.info(self.results.add({"geodata": ras_out, "source_geodata": ras}))

        self.log.debug("OUT")
        return

# import arcpy
# arcpy.Clip_management(
#     "c:/data/image.tif", "1952602 294196 1953546 296176",
#     "c:/data/clip.gdb/clip01", "#", "#", "NONE", "NO_MAINTAIN_EXTENT")

# Clip_management (in_raster, rectangle, out_raster, {in_template_dataset}, {nodata_value}, {clipping_geometry})
# http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/clip.htm#C_GUID-D4B6E476-CD4C-4BAD-A082-F698D0CDEDA6

# Wraps arcpy.Clip_management\n\nsee http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/clip.htm

