from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats
from arcpy.sa import *


tool_settings = {"label": "Lookup by Table",
                 "description": "Lookup by table..",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class LookupByTableRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["lookup fields:table_fields:", "raster:geodata:"])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.lookup, "raster_table", ["table_fields", "geodata"])

        return

    def lookup(self, data):

        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)

        lookup_fields = data["table_fields"].replace(" ", "").split(",")
        for f in lookup_fields:
            try:
                self.info("Lookup field '{0}' in '{1}'".format(f, ras))
                out = Lookup(ras, f)
                ras_out = utils.make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix + "_" + f)
                out.save(ras_out)
                self.info("Saved to {0}".format(ras_out))

                self.result.add_pass({"geodata": ras_out, "source_geodata": ras})
            except:
                self.warn("Failed on field '{}'".format(f))
                data["geodata"] = ras
                data["failure_field"] = f
                self.result.add_fail(data)

        return

# "http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/lookup.htm"

