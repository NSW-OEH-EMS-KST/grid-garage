from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, transform_methods

tool_settings = {"label": "Transform",
                 "description": "Transforms rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
class TransformRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    parameter("transform", "Method", "GPString", "Required", False, "Input", transform_methods, None, None, transform_methods[0])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterate(self):
        self.iterate_function_on_tableview(self.transform, "raster_table", ["raster"])
        return

    def transform(self, data):
        self.send_info(data)
        # self.add_result("TODO")
        return

