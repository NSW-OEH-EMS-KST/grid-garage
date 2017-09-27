import base.base_tool

from base.decorators import input_output_table, input_tableview
from base.utils import describe

tool_settings = {"label": "Describe",
                 "description": "Describes geodata",
                 "can_run_background": "True",
                 "category": "Geodata"}


class DescribeGeodataTool(base.base_tool.BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview()
    @input_output_table
    def getParameterInfo(self):
        """

        Returns:

        """

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.describe, "geodata_table", ["geodata"], return_to_results=True)

        return

    def describe(self, data):
        """

        Args:
            data:

        Returns:

        """

        item = data["geodata"]
        self.info("Describing {0}".format(item))

        return describe(item)

