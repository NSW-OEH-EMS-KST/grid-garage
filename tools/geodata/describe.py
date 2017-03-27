import base.base_tool
import base.results
from base.method_decorators import input_output_table, input_tableview
from base.utils import describe

tool_settings = {"label": "Describe",
                 "description": "Describes geodata",
                 "can_run_background": "True",
                 "category": "Geodata"}


@base.results.result
class DescribeGeodataTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterating]

        return

    @input_tableview("geodata_table", "Table for Geodata", False, ["geodata:geodata:none"])
    @input_output_table
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterating(self):

        self.iterate_function_on_tableview(self.describe, "geodata_table", ["geodata"])

        return

    def describe(self, data):

        item = data["geodata"]
        self.log.info("Describing {0}".format(item))
        r = describe(item)
        self.log.info(self.results.add(r))

        return

