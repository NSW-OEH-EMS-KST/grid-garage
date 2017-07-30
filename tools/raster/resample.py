from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, resample_methods, raster_formats
import arcpy

tool_settings = {"label": "Resample",
                 "description": "Resample rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class ResampleRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("resample_type", "Resampling Method", "GPString", "Required", False, "Input", resample_methods, "resamplingMethod", None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.resample, "raster_table", ["geodata"], return_to_results=True)

        return

    def resample(self, data):

        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)

        ras_out = utils.make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.info("Resampling {0} -->> {1} ...".format(ras, ras_out))

        arcpy.Resample_management(ras, ras_out, self.cell_size, self.resample_type)

        return {"geodata": ras_out, "source_geodata": ras}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/resample.htm"


