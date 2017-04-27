import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats
from arcpy.sa import *
import base.utils


tool_settings = {"label": "Lookup by Table",
                 "description": "Lookup by table..",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class LookupByTableRasterTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["lookup fields:table_fields:", "raster:geodata:"])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.lookup, "raster_table", ["lookup fields", "raster"])

        return

    def lookup(self, data):

        ras = data["raster"]
        base.utils.validate_geodata(ras, raster=True)

        lookup_fields = data["lookup fields"].replace(" ", "").split(",")
        for f in lookup_fields:
            try:
                ras_out = base.utils.make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix + "_" + f)
                self.log.info("Lookup field {0} in {1}".format(f, ras))
                out = Lookup(ras, f)
                self.log.info(out)
                self.log.info("Saving to {0}".format(ras_out))
                out.save(ras_out)
                self.result.add({"geodata": ras_out, "source_geodata": ras})
            except:
                self.log.warn("Failed on field '{}'".format(f))
                self.result.fail(ras, data)

        return

# "http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/lookup.htm"

