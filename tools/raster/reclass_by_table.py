from base.base_tool import BaseTool

from base import utils
from base.decorators import input_tableview, input_output_table_with_output_affixes, parameter, data_nodata, raster_formats
import arcpy

tool_settings = {"label": "Reclass by Table",
                 "description": "Reclass by table...",
                 "can_run_background": "True",
                 "category": "Raster"}


class ReclassByTableRasterTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        self.from_value_field = None
        self.to_value_field = None
        self.output_value_field = None

        return

    @input_tableview(data_type="raster")
    @input_tableview(ob_name="in_remap_table", ob_title="Remap Table", other_fields="output_value_field Output_Value Required output_value, to_value_field To_Value Required to_value, from_value_field From_Value Required from_value")
    @parameter("missing_values", "Missing value treatment", "GPString", "Optional", False, "Input", data_nodata, None, None, data_nodata[0], "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        p = self.get_parameter_dict()

        self.from_value_field = p["in_remap_table_field_from_value_field"]
        self.to_value_field = p["in_remap_table_field_to_value_field"]
        self.output_value_field = p["in_remap_table_field_output_value_field"]

        self.iterate_function_on_tableview(self.reclass, "raster_table", ["geodata"], return_to_results=True)

        return

    def reclass(self, data):
        """

        Args:
            data:

        Returns:

        """

        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)

        ras_out = utils.make_raster_name(ras, self.output_file_workspace, self.raster_format, self.output_filename_prefix, self. output_filename_suffix)

        self.info("Reclassifying {0} -->> {1}...".format(ras, ras_out))

        arcpy.ReclassByTable_3d(ras, self.in_remap_table, self.from_value_field, self.to_value_field, self.output_value_field, ras_out, self.missing_values)

        return {"geodata": ras_out, "source_geodata": ras}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/3d-analyst-toolbox/reclass-by-table.htm"
