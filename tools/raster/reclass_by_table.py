import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, data_nodata, raster_formats
import arcpy
import base.utils

tool_settings = {"label": "Reclass by Table",
                 "description": "Reclass by table...",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class ReclassByTableRasterTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @input_tableview("in_remap_table", "Remap Table", False, ["Output Value::", "To Value::", "From Value::"])
    @parameter("missing_values", "Missing value treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0], "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        # self.in_remap_table = p["in_remap_table"]
        self.from_value_field = p["in_remap_table_field_2"]
        self.to_value_field = p["in_remap_table_field_1"]
        self.output_value_field = p["in_remap_table_field_0"]
        # self.missing_values = p["missing_values"] if p["missing_values"] else "#"
        # self.raster_format = "" if p["raster_format"].lower() == "esri grid" else '.' + p["raster_format"]

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.reclass, "raster_table", ["raster"])

        return

    def reclass(self, data):

        # self.send_info(data)
        ras = data["raster"]
        base.utils.validate_geodata(ras, raster=True)

        ras_out = base.utils.make_raster_name(ras, self.result.output_workspace, self.raster_format)
        self.send_info("Reclassifying {0} -->> {1}...".format(ras, ras_out))
        arcpy.ReclassByTable_3d(ras, self.in_remap_table, self.from_value_field, self.to_value_field, self.output_value_field, ras_out, self.missing_values)

        self.result.add({"geodata": ras_out, "source_geodata": ras})
        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/3d-analyst-toolbox/reclass-by-table.htm"
