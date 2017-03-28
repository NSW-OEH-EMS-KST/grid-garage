import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table, parameter
from arcpy import CalculateStatistics_management

tool_settings = {"label": "Calculate Statistics",
                 "description": "Calculates raster band statistics",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class CalculateStatisticsRasterTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("x_skip_factor", "X Skip Factor", "GPLong", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("y_skip_factor", "Y Skip Factor", "GPLong", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("ignore_values", "Ignore Values", "GPLong", "Optional", True, "Input", None, None, None, None, "Options")
    @parameter("skip_existing", "Existing Statistics", "GPString", "Optional", False, "Input", ["OVERWRITE", "SKIP_EXISTING"], None, None, "OVERWRITE", "Options")
    @parameter("area_of_interest", "Area of Interest", "GPFeatureLayer", "Optional", False, "Input", ["Polygon"], None, None, None, "Options")
    @input_output_table
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.calculate, "raster_table", ["raster"])

        return

    def calculate(self, data):

        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)
        CalculateStatistics_management(ras, self.x_skip_factor, self.y_skip_factor, self.ignore_values, self.skip_existing, self.area_of_interest)

        self.result.add({"geodata": ras, "statistics": "built"})

        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/calculate-statistics.htm"
