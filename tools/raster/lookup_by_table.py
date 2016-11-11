from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, raster_formats
from arcpy.sa import *

tool_settings = {"label": "Lookup by Table",
                 "description": "Lookup by table..",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class LookupByTableRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["lookup fields:table_fields:", "raster:geodata:"])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.raster_format = "" if p["raster_format"].lower() == "esri grid" else '.' + p["raster_format"]

    def iterate(self):
        self.iterate_function_on_tableview(self.lookup, "raster_table", ["lookup fields", "raster"])
        return

    def lookup(self, data):
        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)

        lookup_fields = data["lookup fields"].replace(" ", "").split(",")
        for f in lookup_fields:
            try:
                ras_out = self.geodata.make_raster_name(ras, self.results.output_workspace, self.raster_format, "_" + f)
                self.send_info("Lookup field {0} in {1}".format(f, ras))
                out = Lookup(ras, f)
                self.send_info(out)
                self.send_info("Saving to {0}".format(ras_out))
                out.save(ras_out)
                self.results.add({"geodata": ras_out, "source_geodata": ras})
            except Exception as e:
                self.results.fail(ras, e, data, self)

        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/lookup.htm"

