from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, data_nodata, raster_formats
import arcpy

tool_settings = {"label": "Slice",
                 "description": "Slice raster",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class SliceRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("raster_format", "Output Raster Format", "GPString", "Optional", False, "Input", raster_formats, None, None, "Esri Grid")
    @parameter("num_zones", "Number of Zones", "GPLong", "Required", False, "Input", None, None, None, 10, "Options")
    @parameter("slice_type", "Type of Slice", "GPString", "Required", False, "Input", ["EQUAL_INTERVAL", "EQUAL_AREA", "NATURAL_BREAKS"], None, None, None)
    @parameter("base_output_zone", "Base Output Zone", "GPLong", "Required", False, "Input", None, None, None, 1, "Options")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        # p = self.get_parameter_dict()

        # self.from_value_field = p["in_remap_table_field_from_value_field"]
        # self.to_value_field = p["in_remap_table_field_to_value_field"]
        # self.output_value_field = p["in_remap_table_field_output_value_field"]

        self.iterate_function_on_tableview(self.slice, "raster_table", ["geodata"], return_to_results=True)

        return

    def slice(self, data):

        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)

        ras_out = utils.make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self. output_filename_suffix)

        self.info("Slicing {0} -->> {1}...".format(ras, ras_out))

        arcpy.Slice_3d(ras, ras_out, self.num_zones, self.slice_type, self.base_output_zone)

        return {"geodata": ras_out, "source_geodata": ras}

#  Slice_3d (in_raster, out_raster, number_zones, {slice_type}, {base_output_zone})