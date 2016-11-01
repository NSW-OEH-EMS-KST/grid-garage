from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_tableview, input_output_table, parameter

tool_settings = {"label": "Set NoData Value",
                 "description": "Set NoData Value...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
class SetNodataValueRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.ndv = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("ndv", "NoData Value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.ndv = p["ndv"]

    def iterate(self):
        self.iterate_function_on_tableview(self.set_ndv, "raster_table", ["raster"])
        return

    def set_ndv(self, data):
        self.send_info(data)
        # self.add_result("TODO")
        return

