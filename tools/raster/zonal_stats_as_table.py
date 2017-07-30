from base.base_tool import BaseTool
from base.results import result
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter
import arcpy
from base.utils import validate_geodata, make_table_name, stats_type


tool_settings = {"label": "Zonal Statistics As Table",
                 "description": "Calculate zonal statistics and report in a table",
                 "can_run_background": "True",
                 "category": "Raster"}

# ZonalStatisticsAsTable (in_zone_data, zone_field, in_value_raster, out_table, {ignore_nodata}, {statistics_type})

@result
class ZonalStatisticsAsTableTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.polygon_srs = None

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("zones", "Zones", "GPFeatureLayer", "Required", False, "Input", ["Polygon"], None, None, None, "Options")
    @parameter("zone_field", "Zone Field", "Field", "Required", False, "Input", None, None, ["zones"], None, None)
    @parameter("ignore_no_data", "'NoData' treatment", "GPString", "Optional", False, "Input", ["DATA", "NODATA"], None, None, None, "Options")
    @parameter("statistics_type", "statistics_type", "GPString", "Optional", False, "Input", stats_type, None, None, "ALL", "Options")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.calc, "raster_table", ["geodata"], return_to_results=True)

        return

    def calc(self, data):

        ras = data["geodata"]
        validate_geodata(ras, raster=True)

        ras_out = make_table_name(ras, self.result.output_workspace, None, self.output_filename_prefix, self. output_filename_suffix)

        self.info("Extracting stats table {0} -->> {1} ...".format(ras, ras_out))

        # ZonalStatisticsAsTable (in_zone_data, zone_field, in_value_raster, out_table, {ignore_nodata}, {statistics_type})
        arcpy.sa.ZonalStatisticsAsTable(self.zones, self.zone_field, ras, ras_out, self.ignore_no_data, self.statistics_type)

        return {"geodata": ras_out, "source_geodata": ras}
