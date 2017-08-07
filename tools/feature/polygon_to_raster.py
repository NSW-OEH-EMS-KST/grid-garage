from base.base_tool import BaseTool
import base.results
from base.method_decorators import input_output_table_with_output_affixes, input_tableview, parameter, raster_formats
from os.path import splitext
from arcpy import PolygonToRaster_conversion
import base.utils


tool_settings = {"label": "Polygon to Raster",
                 "description": "Rasterise polygon features by a 'field of fields' and additional geometry options",
                 "can_run_background": "True",
                 "category": "Feature"}


@base.results.result
class PolygonToRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("features_table", "Table for Features and Fields", False, ["priority field:priority_field:Optional", "fields:table_fields:", "feature:geodata:"])
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @parameter("cell_assignment", "Cell Assignment", "GPString", "Optional", False, "Input", ["CELL_CENTER", "MAXIMUM_AREA", "MAXIMUM_COMBINED_AREA"], None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        self.info(self.get_parameter_dict())

        self.cell_assignment = "CELL_CENTER" if self.cell_assignment in [None, "#"] else self.cell_assignment

        self.iterate_function_on_tableview(self.rasterise, "features_table", ["geodata", "table_fields", "priority_field"])

        return

    def rasterise(self, data):
        self.info(data)

        feat_ds = data["geodata"]
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
            # self.warn("")
            pass

        for field in target_fields:
            try:
                r_out = base.utils.make_raster_name("{0}_{1}".format(splitext(feat_ds)[0], field), self.output_file_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
                self.info("Rasterising {} on {} with priority field {} -> {}".format(feat_ds, field, priority_field, r_out))
                PolygonToRaster_conversion(feat_ds, field, r_out, self.cell_assignment, priority_field, self.cell_size)
                self.result.add_pass({"geodata": r_out, "source_geodata": feat_ds, "source_field": field, "priority_field": priority_field})
            except Exception as e:
                self.error("FAILED rasterising {} on {} priority {}: {}".format(feat_ds, field, priority_field, str(e)))
                self.result.add_fail(data)

#    PolygonToRaster_conversion (in_features, value_field, out_rasterdataset, {cell_assignment}, {priority_field}, {cellsize})