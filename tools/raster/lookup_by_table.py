from base.base_tool import BaseTool

from base import utils
from base.decorators import input_tableview, input_output_table, parameter, raster_formats
from arcpy.sa import *


tool_settings = {"label": "Lookup by Table",
                 "description": "Lookup by table..",
                 "can_run_background": "True",
                 "category": "Raster"}



class LookupByTableRasterTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="raster", other_fields="table_fields Lookup_Fields Required table_fields")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table(affixing=True)
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.lookup)

        return

    def lookup(self, data):
        """

        Args:
            data:

        Returns:

        """

        ras = data["raster"]

        utils.validate_geodata(ras, raster=True)

        ws = self.output_file_workspace or self.output_workspace

        lookup_fields = data["table_fields"].replace(" ", "").split(",")
        for f in lookup_fields:
            try:
                self.info("Lookup field '{0}' in '{1}'".format(f, ras))
                out = Lookup(ras, f)
                ras_out = utils.make_raster_name(ras, ws, self.raster_format, self.output_filename_prefix, self.output_filename_suffix + "_" + f)
                out.save(ras_out)
                self.info("Saved to {0}".format(ras_out))

                self.result.add_pass({"raster": ras_out, "source_geodata": ras})
            except:
                self.warn("Failed on field '{}'".format(f))
                data["raster"] = ras
                data["failure_field"] = f
                self.result.add_fail(data)

        return

# "http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/lookup.htm"

