from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter
from arcpy import CalculateStatistics_management

tool_settings = {"label": "Calculate Statistics",
                 "description": "Calculates raster band statistics",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class CalculateStatisticsRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.x_skip_factor = None
        self.y_skip_factor = None
        self.ignore_values = None
        self.skip_existing = None
        self.area_of_interest = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("x_skip_factor", "X Skip Factor", "GPLong", "Optional", False, "Input", None, None, None, None)
    @parameter("y_skip_factor", "Y Skip Factor", "GPLong", "Optional", False, "Input", None, None, None, None)
    @parameter("ignore_values", "Ignore Values", "GPLong", "Optional", True, "Input", None, None, None, None)
    @parameter("skip_existing", "Existing Statistics", "GPString", "Optional", False, "Input", ["OVERWRITE", "SKIP_EXISTING"], None, None, "OVERWRITE")
    @parameter("area_of_interest", "Area of Interest", "GPFeatureLayer", "Optional", False, "Input", ["Polygon"], None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.x_skip_factor = p["x_skip_factor"] if p["x_skip_factor"] else "#"
        self.y_skip_factor = p["y_skip_factor"] if p["y_skip_factor"] else "#"
        self.x_skip_factor = p["ignore_values"] if p["ignore_values"] else "#"
        self.x_skip_factor = p["x_skip_factor"] if p["x_skip_factor"] else "#"
        self.x_skip_factor = p["skip_existing"] if p["skip_existing"] else "#"
        self.x_skip_factor = p["area_of_interest"] if p["area_of_interest"] else "#"

    def iterate(self):
        self.iterate_function_on_tableview(self.calculate, "raster_table", ["raster"])
        return

    def calculate(self, data):
        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)
        CalculateStatistics_management(ras, self.x_skip_factor, self.y_skip_factor, self.ignore_values, self.skip_existing, self.area_of_interest)
        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/calculate-statistics.htm"
