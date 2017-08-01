import base.base_tool
import base.results
from base.method_decorators import input_output_table, parameter
from base.utils import datatype_list, walk
tool_settings = {"label": "Search",
                 "description": "Search for identifiable geodata",
                 "can_run_background": "True",
                 "category": "Geodata"}

@base.results.result
class SearchGeodataTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @parameter("workspaces", "Workspaces to Search", "DEWorkspace", "Required", True, "Input", None, None, None, None)
    @parameter("geodata_types", "Data Types", "GPString", "Required", True, "Input", datatype_list, None, None, None)
    @input_output_table
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def initialise(self):

        gt = self.geodata_types.split(";")
        gt = ["Any"] if "Any" in gt else gt
        self.geodata_types = gt

        return

    def iterate(self):
        self.iterate_function_on_parameter(self.search, "workspaces", ["workspace"])

        return

    def search(self, data):

        ws = data["workspace"]

        for dt in self.geodata_types:
            self.info("Searching for {0} geodata types in {1}".format(dt, ws))
            found = [{"geodata": v} for v in walk(ws.strip("'"), data_types=dt)]
            if not found:
                self.info("Nothing found")
            else:
                self.info(self.result.add(found))

        return
