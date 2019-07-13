from base.base_tool import BaseTool
from base.decorators import input_output_table, parameter
from base.utils import walk

tool_settings = {"label": "Search for Features",
                 "description": "Search for identifiable feature classes",
                 "can_run_background": "True",
                 "category": "Feature"}


class SearchFeaturesTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @parameter("workspaces", "Workspaces to Search", "DEWorkspace", "Required", True, "Input", None, None, None, None)
    @input_output_table()
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_parameter(self.search, "workspaces", ["workspace"])

        return

    def search(self, data):
        """

        Args:
            data:

        Returns:

        """

        ws = data["workspace"]

        self.info("Searching for features in {}".format(ws))

        found = [{"feature": f} for f in walk(ws.strip("'"), data_types="FeatureClass")]

        self.result.add_pass(found)

        return
