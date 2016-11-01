from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter

tool_settings = {"label": "Set Value to Null",
                 "description": "Sets...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class SetValueToNullRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.val_to_null = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("val_to_null", "Value to Set Null", "GPDouble", "Required", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.val_to_null = p["val_to_null"]

    def iterate(self):
        self.iterate_function_on_tableview(self.process, "raster_table", ["raster"])
        return

    def process(self, data):
        self.send_info(data)
        # TODO
        return


