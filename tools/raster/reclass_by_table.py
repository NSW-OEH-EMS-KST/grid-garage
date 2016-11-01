from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, data_nodata
from arcpy import ReclassByTable_3d

tool_settings = {"label": "Reclass by Table",
                 "description": "Reclass by table...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class ReclassByTableRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.in_remap_table = None
        self.from_value_field = None
        self.to_value_field = None
        self.output_value_field = None
        self.missing_values = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("in_remap_table", "Remap Table", "DETable", "Required", False, "Input", None, None, ["from_value_field", "from_value_field", "output_value_field"], None)
    @parameter("from_value_field", "From Value Field", "Field", "Required", False, "Input", None, None, None, None)
    @parameter("to_value_field", "To Value Field", "Field", "Required", False, "Input", None, None, None, None)
    @parameter("output_value_field", "Output Value Field", "Field", "Required", False, "Input", None, None, None, None)
    @parameter("missing_values", "Missing value treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.in_remap_table = p["in_remap_table"]
        self.from_value_field = p["from_value_field"]
        self.to_value_field = p["to_value_field"]
        self.output_value_field = p["output_value_field"]
        self.missing_values = p["missing_values"] if p["missing_values"] else "#"

    def iterate(self):
        self.iterate_function_on_tableview(self.reclass, "raster_table", ["raster"])
        return

    def reclass(self, data):
        self.send_info(data)
        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)

        ras_out = self.geodata.make_raster_name(ras, self.results.output_workspace, self.raster_format)
        self.send_info("Reclassifying {0} -->> {1} ...".format(ras, ras_out))
        ReclassByTable_3d(ras, self.in_remap_table, self.from_value_field, self.to_value_field, self.output_value_field, ras_out, self.missing_values)

        self.results.add({"geodata": ras_out, "source_geodata": ras})
        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/3d-analyst-toolbox/reclass-by-table.htm"
