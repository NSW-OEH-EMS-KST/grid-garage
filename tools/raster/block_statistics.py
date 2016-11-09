from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, stats_type, data_nodata, raster_formats
from arcpy.sa import BlockStatistics

tool_settings = {"label": "Block Statistics",
                 "description": "Block Statistics...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class BlockStatisticsRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.neighbourhood = None
        self.statistics_type = None
        self.ignore_nodata = None
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("neighbourhood", "Neighbourhood", "GPSANeighborhood", "Required", False, "Input", None, None, None, None)
    @parameter("statistics_type", "Statistics", "GPString", "Optional", False, "Input", stats_type, None, None, stats_type[0])
    @parameter("ignore_nodata", "No Data Treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.neighbourhood = p["neighbourhood"]
        self.statistics_type = p["statistics_type"] if p["statistics_type"] else "#"
        self.ignore_nodata = p["ignore_nodata"] if p["ignore_nodata"] else "#"
        self.raster_format = p["raster_format"]

    def iterate(self):
        self.iterate_function_on_tableview(self.block_statistics, "raster_table", ["raster"])
        return

    def block_statistics(self, data):
        self.send_info(data)
        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)

        tbl_out = self.geodata.make_table_name(ras, self.results.output_workspace, self.raster_format)
        self.send_info("Calculating block statistics on {0}...".format(ras))

        out = BlockStatistics(ras, self.neighbourhood, self.statistics_type, self.ignore_nodata)
        out.save(tbl_out)

        self.results.add({"geodata": tbl_out, "source_geodata": ras})
        return


"http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/block-statistics.htm"

