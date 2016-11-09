from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, raster_formats, aggregation_methods, data_nodata, expand_trunc
from arcpy.sa import Aggregate

tool_settings = {"label": "Aggregate",
                 "description": "Aggegate raster values...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class AggregateRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.cell_factor = None
        self.aggregation_type = None
        self.extent_handling = None
        self.ignore_nodata = None
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("cell_factor", "Cell Aggregation Factor", "GPLong", "Required", False, "Input", ["Range", 2, 1000], None, None, None)
    @parameter("aggregation_type", "Aggregation Method", "GPString", "Optional", False, "Input", aggregation_methods, None, None, aggregation_methods[0])
    @parameter("extent_handling", "Extent Boundary", "GPString", "Optional", False, "Input", expand_trunc, None, None, expand_trunc[0])
    @parameter("ignore_nodata", "No Data Treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.cell_factor = p["cell_factor"]
        self.aggregation_type = p["aggregation_type"] if p["aggregation_type"] else "#"
        self.extent_handling = p["extent_handling"] if p["extent_handling"] else "#"
        self.ignore_nodata = p["ignore_nodata"] if p["ignore_nodata"] else "#"
        self.raster_format = p["raster_format"]

    def iterate(self):
        self.iterate_function_on_tableview(self.aggregate, "raster_table", ["raster"])
        return

    def aggregate(self, data):
        self.send_info(data)
        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)

        ras_out = self.geodata.make_raster_name(ras, self.results.output_workspace, self.raster_format)
        self.send_info("Aggregating {0} -->> {1} ...".format(ras, ras_out))
        # Aggregate(in_raster, cell_factor, {aggregation_type}, {extent_handling}, {ignore_nodata})
        out = Aggregate(ras, self.cell_factor, self.aggregation_type, self.extent_handling, self.ignore_nodata)
        out.save(ras_out)

        self.results.add({"geodata": ras_out, "source_geodata": ras})
        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/aggregate.htm"
