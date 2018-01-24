import base.base_tool
import base.results
from base.method_decorators import input_output_table, parameter

tool_settings = {"label": "Select",
                 "description": "Feed selected geodata into a table",
                 "can_run_background": "True",
                 "category": "Geodata"}


@base.results.result
class SelectGeodataTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @parameter("geodata", "Select Geodata", "GPType", "Required", True, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_parameter(self.process, "geodata", ["geodata"])

        return

    def process(self, data):

        self.result.add_pass(data)

        return

