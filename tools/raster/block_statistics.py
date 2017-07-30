from base.base_tool import BaseTool
from base.results import result
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, stats_type, data_nodata, raster_formats
from arcpy.sa import BlockStatistics
from base.utils import validate_geodata, make_raster_name

tool_settings = {"label": "Block Statistics",
                 "description": "Block Statistics...",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class BlockStatisticsRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("neighbourhood", "Neighbourhood", "GPSANeighborhood", "Required", False, "Input", None, None, None, None)
    @parameter("statistics_type", "Statistics", "GPString", "Optional", False, "Input", stats_type, None, None, stats_type[0], "Options")
    @parameter("ignore_nodata", "No Data Treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0], "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.block_statistics, "raster_table", ["geodata"], return_to_results=True)

        return

    def block_statistics(self, data):

        ras = data["geodata"]

        validate_geodata(ras, raster=True)

        ras_out = make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.info("Calculating block statistics on {0}...".format(ras))

        out = BlockStatistics(ras, self.neighbourhood, self.statistics_type, self.ignore_nodata)

        self.info("Saving to {0}...".format(ras_out))

        out.save(ras_out)

        return {"geodata": ras_out, "source_geodata": ras}


# "http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/block-statistics.htm"

