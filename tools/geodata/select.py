from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_output_table, parameter

tool_settings = {"label": "Select",
                 "description": "Feed selected geodata into a table",
                 "can_run_background": "True",
                 "category": "Geodata"}


@results
class SelectGeodataTool(BaseTool):

    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.start_iteration]

    @parameter("geodata", "Select Geodata", "GPType", "Required", True, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def start_iteration(self):
        self.iterate_function_on_parameter(self.process, "geodata", ["geodata"])
        return

    def process(self, data):
        self.results.add(data)
        return

