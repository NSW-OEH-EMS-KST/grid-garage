from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table, parameter
import arcpy


tool_settings = {"label": "Build Attribute Table",
                 "description": "Builds attribute tables for rasters",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class BuildAttributeTableRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("overwrite", "Overwrite existing table", "GPBoolean", "Required", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.overwrite = "Overwrite" if self.overwrite else "NONE"

        self.iterate_function_on_tableview(self.build_rat, "raster_table", ["geodata"], return_to_results=True)

        return

    def build_rat(self, data):

        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)

        self.info("Building attribute table for {0}...".format(ras))

        arcpy.BuildRasterAttributeTable_management(ras, self.overwrite)

        return {"geodata": ras, "attribute_table": "built"}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/build-raster-attribute-table.htm"
