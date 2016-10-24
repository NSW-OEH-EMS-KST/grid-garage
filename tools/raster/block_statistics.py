from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_tableview, input_output_table

tool_settings = {"label": "Block Statistics",
                 "description": "Block Statistics...",
                 "can_run_background": "True",
                 "category": "Raster TODO"}


@results
class BlockStatisticsRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.start_iteration]

    @input_tableview(name="geodata_table", display_name="Table of Geodata", multi_value=False, required_fields=["raster:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def start_iteration(self):
        self.iterate_function_on_parameter(self.process, "geodata_table", ["geodata"])
        return

    def process(self, data):
        self.send_info(data)
        return

