from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview

tool_settings = {"label": "Describe",
                 "description": "Describes geodata",
                 "can_run_background": False,
                 "category": "Geodata"}


@geodata
@results
class DescribeGeodataTool(BaseTool):

    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterating]

    @input_tableview("geodata_table", "Table for Geodata", False, ["geodata:geodata:none"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterating(self):
        self.iterate_function_on_tableview(self.describe, "geodata_table", ["geodata"])

    def describe(self, data):
        item = data["geodata"]
        self.send_info("Describing {0}".format(item))
        r = self.geodata.describe(item)
        self.results.add(r)

