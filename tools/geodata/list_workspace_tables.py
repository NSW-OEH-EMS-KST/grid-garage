from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, parameter
from base.utils import split_up_filename
import re

tool_settings = {"label": "List Workspace Tables",
                 "description": "List tables within a workspace",
                 "can_run_background": "True",
                 "category": "Geodata"}


@geodata
@results
class ListWorkspaceTablesGeodataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @parameter("workspaces", "Workspaces", "DEWorkspace", "Required", True, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterate(self):
        self.iterate_function_on_parameter(self.list, "workspaces", ["workspace"])

    def list(self, data):
        # ws = self.get_parameter_by_name("workspace").valueAsText
        ws = data["workspace"]
        self.send_info("Searching for tables in {0}".format(ws))
        found = self.geodata.walk(ws, data_types="Table")
        self.send_info(found)
        if not found:
            self.send_info("No tables were found")
            return

        dic_list = []
        for f in found:
            f_ws, f_base, f_name, f_ext = split_up_filename(f)
            d = {"geodata": f, "table_name": f_base}
            match = re.search(r'\d{8}_\d{6}', f_base)
            d["date_time_ex_name"] = match.group(0) if match else None
            dic_list.append(d)

        self.send_info(dic_list)
        self.send_info(self.results.add(dic_list))
        return
