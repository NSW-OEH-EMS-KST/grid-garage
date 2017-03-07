from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_output_table, input_tableview
from base.utils import describe

tool_settings = {"label": "Describe",
                 "description": "Describes geodata",
                 "can_run_background": "True",
                 "category": "Geodata"}


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
        self.log.info("Describing {0}".format(item))
        r = describe(item)
        self.log.info(self.results.add(r))

