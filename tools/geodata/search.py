from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, parameter
from base.geodata import datatype_list

tool_settings = {"label": "Search",
                 "description": "Search for identifiable geodata",
                 "can_run_background": False,
                 "category": "Geodata"}


@geodata
@results
class SearchGeodataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterating]
        self.geodata_types = []

    @parameter("workspaces", "Workspaces to Search", "DEWorkspace", "Required", True, "Input", None, None, None, None)
    @parameter("geodata_types", "Data Types", "GPString", "Required", True, "Input", datatype_list, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        gt = p.get("geodata_types", "")
        gt = gt.split(";")
        self.geodata_types = gt

    def iterating(self):
        self.iterate_function_on_parameter(self.search, "workspaces", ["workspace"])

    def search(self, data):
        ws = data["workspace"]
        for dt in self.geodata_types:
            self.send_info("Searching for {0} geodata types in {1}".format(dt, ws))
            found = [{"geodata": v} for v in self.geodata.walk(ws, data_types=dt)]
            if not found:
                self.send_info("Nothing found")
            else:
                self.send_info(self.results.add(found))

        return
