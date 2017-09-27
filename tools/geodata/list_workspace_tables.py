from base.base_tool import BaseTool
from base.decorators import input_output_table, parameter
from base.utils import split_up_filename, walk
import re


tool_settings = {"label": "List Workspace Tables",
                 "description": "List tables within a workspace",
                 "can_run_background": "True",
                 "category": "Geodata"}


class ListWorkspaceTablesGeodataTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @parameter("workspaces", "Workspaces", "DEWorkspace", "Required", True, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        """

        self.iterate_function_on_parameter(self.list, "workspaces", ["workspace"], return_to_results=True)

    def list(self, data):
        """

        Args:
            data:

        Returns:

        """

        ws = data["workspace"]
        self.info("Searching for tables in {0}".format(ws))
        found = walk(ws.strip("'"), data_types="Table")
        [self.info("Found: {}".format(f)) for f in found]
        if not found:
            self.info("No tables were found")
            return

        dic_list = []
        for f in found:
            f_ws, f_base, f_name, f_ext = split_up_filename(f)
            d = {"geodata": f, "table_name": f_base}
            match = re.search(r'\d{8}_\d{6}', f_base)
            d["date_time_ex_name"] = match.group(0) if match else None
            dic_list.append(d)

        return dic_list
