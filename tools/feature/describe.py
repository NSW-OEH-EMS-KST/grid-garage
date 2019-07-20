import base.base_tool

from base.decorators import input_output_table, input_tableview
from base.utils import describe

tool_settings = {"label": "Describe Features",
                 "description": "Describes feature class properties",
                 "can_run_background": "True",
                 "category": "Feature"}


class DescribeFeatureTool(base.base_tool.BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="feature")
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

        feat_ds = data["feature"]
        base.utils.validate_geodata(feat_ds, vector=True)
        self.info("Describing {0}".format(feat_ds))

        return describe(feat_ds, feature=True)

