from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_tableview, input_output_table

tool_settings = {"label": "Lookup by Table",
                 "description": "Lookup by table..",
                 "can_run_background": "True",
                 "category": "Raster TODO"}


@results
class LookupByTableRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.start_iteration]

    @input_tableview("geodata_table", "Table of Geodata", False, ["raster:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def start_iteration(self):
        self.iterate_function_on_parameter(self.process, "geodata_table", ["geodata"])
        return

    def process(self, data):
        self.send_info(data)
        # TODO
        return

