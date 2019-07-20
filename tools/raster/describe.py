import base.base_tool

from base.decorators import input_output_table, input_tableview
from base.utils import describe

tool_settings = {"label": "Describe Rasters",
                 "description": "Describes raster properties",
                 "can_run_background": "True",
                 "category": "Raster"}


class DescribeRasterTool(base.base_tool.BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="raster")
    @input_output_table()
    def getParameterInfo(self):
        """

        Returns:

        """

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.describe, return_to_results=True)

        return

    def describe(self, data):
        """

        Args:
            data:

        Returns:

        """

        ras_ds = data["raster"]
        self.info("Describing {0}".format(ras_ds))

        return describe(ras_ds, raster=True)

