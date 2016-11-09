from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter
from arcpy import BuildRasterAttributeTable_management

tool_settings = {"label": "Build Attribute Table",
                 "description": "Builds attribute tables for rasters",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class BuildAttributeTableRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.overwrite = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("overwrite", "Overwrite existing table", "GPBoolean", "Required", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.overwrite = "Overwrite" if p["overwrite"] else "NONE"

    def iterate(self):
        self.iterate_function_on_tableview(self.build_rat, "raster_table", ["raster"])
        return

    def build_rat(self, data):
        ras = data["raster"]
        self.geodata.validate_geodata(ras, raster=True)

        self.send_info("Building attribute table for {0}...".format(ras))
        BuildRasterAttributeTable_management(ras, self.overwrite)

        self.results.add({"geodata": ras, "attribute_table": "built"})
        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/build-raster-attribute-table.htm"
