import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, resample_methods, raster_formats
import arcpy
import base.utils

tool_settings = {"label": "Resample",
                 "description": "Resample rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class ResampleRasterTool(base.base_tool.BaseTool):

    def __init__(self):
        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("resample_type", "Resampling Method", "GPString", "Required", False, "Input", resample_methods, "resamplingMethod", None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.resample, "raster_table", ["raster"])

        return

    def resample(self, data):

        ras = data["raster"]
        base.utils.validate_geodata(ras, raster=True)
        ras_out = base.utils.make_raster_name(ras, self.results.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.log.info("Resampling {0} -->> {1} ...".format(ras, ras_out))
        arcpy.Resample_management(ras, ras_out, self.cell_size, self.resample_type)

        self.log.info(self.results.add({"geodata": ras_out, "source_geodata": ras}))

        return

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/resample.htm"


