from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table
from arcpy.sa import Lookup

tool_settings = {"label": "Lookup by Table",
                 "description": "Lookup by table..",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class LookupByTableRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("raster_table", "Table for Rasters", False, ["lookup fields:fields:", "raster:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterate(self):
        self.iterate_function_on_tableview(self.lookup, "raster_table", ["raster", "lookup fields"])
        return

    def lookup(self, data):
        self.send_info(data)
        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)
        fields = data["lookup fields"]
        for f in fields:
            ras_out = self.geodata.make_raster_name(ras, self.results.output_workspace, self.raster_format)
            self.send_info("Looking up field {0} in {1} -->> {2}".format(f, ras, ras_out))
            out = Lookup(ras, f)
            out.save(ras_out)
            self.results.add({"geodata": ras_out, "source_geodata": ras})

        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/lookup.htm"

