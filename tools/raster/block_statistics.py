import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, stats_type, data_nodata, raster_formats
from arcpy.sa import BlockStatistics
from base.utils import validate_geodata, make_raster_name

tool_settings = {"label": "Block Statistics",
                 "description": "Block Statistics...",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class BlockStatisticsRasterTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("neighbourhood", "Neighbourhood", "GPSANeighborhood", "Required", False, "Input", None, None, None, None)
    @parameter("statistics_type", "Statistics", "GPString", "Optional", False, "Input", stats_type, None, None, stats_type[0])
    @parameter("ignore_nodata", "No Data Treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.block_statistics, "raster_table", ["raster"])

        return

    def block_statistics(self, data):

        ras = data["raster"]
        validate_geodata(ras, raster=True)

        ras_out = make_raster_name(ras, self.results.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
        self.log.info("Calculating block statistics on {0}...".format(ras))

        out = BlockStatistics(ras, self.neighbourhood, self.statistics_type, self.ignore_nodata)

        self.log.info("Saving to {0}...".format(ras_out))
        out.save(ras_out)

        r = self.results.add({"geodata": ras_out, "source_geodata": ras})
        self.log.info(r)

        return


# "http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/block-statistics.htm"

