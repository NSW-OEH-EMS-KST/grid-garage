from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats, aggregation_methods, data_nodata, expand_trunc
from arcpy.sa import Aggregate


tool_settings = {"label": "Aggregate",
                 "description": "Aggegate raster values...",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class AggregateRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("cell_factor", "Cell Aggregation Factor", "GPLong", "Required", False, "Input", ["Range", 2, 1000], None, None, None)
    @parameter("aggregation_type", "Aggregation Method", "GPString", "Optional", False, "Input", aggregation_methods, None, None, aggregation_methods[0], "Options")
    @parameter("extent_handling", "Extent Boundary", "GPString", "Optional", False, "Input", expand_trunc, None, None, expand_trunc[0], "Options")
    @parameter("ignore_nodata", "No Data Treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0], "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.aggregate, "raster_table", ["geodata"], return_to_results=True)

        return

    def aggregate(self, data):

        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)

        ras_out = utils.make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.info("Aggregating {} -->> {} ...".format(ras, ras_out))

        out = Aggregate(ras, self.cell_factor, self.aggregation_type, self.extent_handling, self.ignore_nodata)

        out.save(ras_out)

        return {"geodata": ras_out, "source_geodata": ras}


# "http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/aggregate.htm"
#  Aggregate (in_raster, cell_factor, {aggregation_type}, {extent_handling}, {ignore_nodata})