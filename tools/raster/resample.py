from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_tableview, input_output_table, parameter, resample_methods, raster_formats
from arcpy import Resample_management
from base.utils import validate_geodata, make_raster_name

tool_settings = {"label": "Resample",
                 "description": "Resample rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
class ResampleRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("resample_type", "Resampling Method", "GPString", "Required", False, "Input", resample_methods, "resamplingMethod", None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterate(self):
        self.iterate_function_on_tableview(self.resample, "raster_table", ["raster"])
        return

    def resample(self, data):
        self.log.debug("IN data={}".format(data))

        ras = data["raster"]
        validate_geodata(ras, raster=True)
        ras_out = make_raster_name(ras, self.results.output_workspace, self.raster_format)

        self.log.info("Resampling {0} -->> {1} ...".format(ras, ras_out))
        Resample_management(ras, ras_out, self.cell_size, self.resample_type)

        self.log.info(self.results.add({"geodata": ras_out, "source_geodata": ras}))

        self.log.debug("OUT")
        return

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/resample.htm"


