from base.base_tool import BaseTool
from base.decorators import input_output_table, input_tableview, parameter, raster_formats
from os.path import splitext
from arcpy import PolygonToRaster_conversion
import base.utils


tool_settings = {"label": "Polygon to Raster",
                 "description": "Rasterise polygon features by a 'field of fields' and additional geometry options",
                 "can_run_background": "True",
                 "category": "Feature"}


class PolygonToRasterTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="feature", other_fields="table_fields Burn_Fields Required table_fields, priority_field Priority_Field Optional None")
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @parameter("cell_assignment", "Cell Assignment", "GPString", "Optional", False, "Input", ["CELL_CENTER", "MAXIMUM_AREA", "MAXIMUM_COMBINED_AREA"], None, None, None)
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

        self.cell_assignment = "CELL_CENTER" if self.cell_assignment in [None, "#"] else self.cell_assignment

        self.iterate_function_on_tableview(self.rasterise)  #, "feature_table", ["feature", "table_fields", "priority_field"])

        return

    def rasterise(self, data):
        """

        Args:
            data:
        """
        self.info(data)

        feat_ds = data["feature"]
        base.utils.validate_geodata(feat_ds, vector=True, polygon=True)

        fields_string = data["table_fields"]
        try:
            target_fields = [field.strip() for field in fields_string.split(",")]
        except:
            raise ValueError("Could not evaluate fields string '{0}'".format(fields_string))

        if not target_fields:
            raise ValueError("No target fields '{0}'".format(target_fields))

        priority_field = None
        try:
            priority_field = data["priority_field"] if data["priority_field"] else priority_field
        except:
            pass

        self.info("Fields to burn for '{0}' are {1}".format(feat_ds, target_fields))

        ws = self.output_file_workspace or self.output_workspace

        for field in target_fields:
            try:
                r_out = base.utils.make_raster_name("{0}_{1}".format(splitext(feat_ds)[0], field), ws, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
                self.info("Rasterising {} on {} with priority field {} -> {}".format(feat_ds, field, priority_field, r_out))
                PolygonToRaster_conversion(feat_ds, field, r_out, self.cell_assignment, priority_field, self.cell_size)
                self.result.add_pass({"geodata": r_out, "source_geodata": feat_ds, "source_field": field, "priority_field": priority_field})
            except Exception as e:
                self.error("FAILED rasterising {} on {} priority {}: {}".format(feat_ds, field, priority_field, str(e)))
                self.result.add_fail(data)

#    PolygonToRaster_conversion (in_features, value_field, out_rasterdataset, {cell_assignment}, {priority_field}, {cellsize})
