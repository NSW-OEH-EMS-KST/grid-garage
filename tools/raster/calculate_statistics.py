from base.base_tool import BaseTool

from base import utils
from base.decorators import input_tableview, input_output_table, parameter
from arcpy import CalculateStatistics_management


tool_settings = {"label": "Calculate Statistics",
                 "description": "Calculates raster band statistics",
                 "can_run_background": "True",
                 "category": "Raster"}


class CalculateStatisticsRasterTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="raster")
    @parameter("x_skip_factor", "X Skip Factor", "GPLong", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("y_skip_factor", "Y Skip Factor", "GPLong", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("ignore_values", "Ignore Values", "GPLong", "Optional", True, "Input", None, None, None, None, "Options")
    @parameter("skip_existing", "Existing Statistics", "GPString", "Optional", False, "Input", ["OVERWRITE", "SKIP_EXISTING"], None, None, "OVERWRITE", "Options")
    @parameter("area_of_interest", "Area of Interest", "GPFeatureLayer", "Optional", False, "Input", ["Polygon"], None, None, None, "Options")
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

        self.iterate_function_on_tableview(self.calculate, return_to_results=True)

        return

    def calculate(self, data):
        """

        Args:
            data:

        Returns:

        """

        ras = data["raster"]

        utils.validate_geodata(ras, raster=True)

        CalculateStatistics_management(ras, self.x_skip_factor, self.y_skip_factor, self.ignore_values, self.skip_existing, self.area_of_interest)

        return {"raster": ras, "statistics": "built"}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/calculate-statistics.htm"
