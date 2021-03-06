from base.base_tool import BaseTool

from base.decorators import input_tableview, input_output_table, parameter
import arcpy
from base.utils import validate_geodata, make_table_name, stats_type


tool_settings = {"label": "Zonal Statistics As Table",
                 "description": "Calculate zonal statistics and report into a table",
                 "can_run_background": "True",
                 "category": "Raster"}


class ZonalStatisticsAsTableTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.polygon_srs = None

        return

    @input_tableview(data_type="raster")
    @parameter("zones", "Zone Features", ["DERasterDataset", "GPFeatureLayer"], "Required", False, "Input", None, None, None, None, None)
    @parameter("zone_field", "Zone Field", "Field", "Required", False, "Input", None, None, ["zones"], None, None)
    @parameter("ignore_no_data", "'NoData' treatment", "GPString", "Optional", False, "Input", ["DATA", "NODATA"], None, None, None, "Options")
    @parameter("statistics_type", "statistics_type", "GPString", "Optional", False, "Input", stats_type + ["ALL"], None, None, "ALL", "Options")
    @input_output_table(affixing=True)
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.calc, return_to_results=True)

        return

    def calc(self, data):
        """

        Args:
            data:

        Returns:

        """

        ras = data["raster"]

        validate_geodata(ras, raster=True)

        tab_out = make_table_name(ras, self.output_file_workspace, None, self.output_file_workspace, self. output_filename_suffix)

        self.info("Extracting statistics from raster '{0}' into table '{1}' ...".format(ras, tab_out))

        arcpy.sa.ZonalStatisticsAsTable(self.zones, self.zone_field, ras, tab_out, self.ignore_no_data, self.statistics_type)

        return {"geodata": tab_out, "source_geodata": ras, "zones": self.zones, "zone_field": self.zone_field, "no_data_handling": self.ignore_no_data, "statistics_type": self.statistics_type}
