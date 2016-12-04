from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter

tool_settings = {"label": "Zonal Counts",
                 "description": "Zonal counts...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class ZonalCountsRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.zone = None
        self.zone_field = None
        self.zone_vals = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("zone", "Zone Features", "GPFeatureLayer", "Required", False, "Input", ["Polygon"], None, None, None)
    @parameter("zone_field", "Field of Interest", "GPString", "Required", False, "Input", None, None, ["zone"], None)
    @parameter("zone_vals", "Values to Count", "GPString", "Required", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.zone = p["zone"]
        self.zone_field = p["zone_field"]
        self.zone_vals = p["zone_vals"]

    def iterate(self):
        self.iterate_function_on_tableview(self.count, "raster_table", ["raster"])
        return

    def count(self, data):
        self.send_info(data)
        # self.add_result("TODO")
        return

