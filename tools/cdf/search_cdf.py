from base.base_tool import BaseTool
from base.decorators import input_output_table, parameter
from os import walk
from os.path import join
from netCDF4 import Dataset


tool_settings = {"label": "Search",
                 "description": "Search for CDF files",
                 "can_run_background": "True",
                 "category": "NetCDF"}


class SearchCdfTool(BaseTool):
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
    @parameter("validate", "Do validation", "GPBoolean", "Optional", False, "Input", None, None, None, None)
    @input_output_table
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

        self.info("Searching for CDF files in {}".format(ws))

        found = []
        for root, directories, filenames in walk(ws):
            for filename in filenames:
                if filename.endswith(".nc"):
                    found.append({"cdf": join(root, filename)})

        if not found:

            self.info("Nothing found")

        else:
            if self.validate:

                to_validate = [f["cdf"] for f in found]

                for v in to_validate:
                    self.info("Validating {}".format(v))

                    if self.valid(v):
                        self.result.add_pass({"cdf": v})
                    else:
                        self.result.add_fail(data)

            else:
                # for f in found:
                self.result.add_pass(found)

        return

    def valid(self, cdf):
        """

        Args:
            cdf:

        Returns:

        """
        try:
            ds = Dataset(cdf)
            del ds
            return True

        except Exception as e:
            self.warn("Validation failed on '{}'".format(cdf))
            return False
