from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_output_table, input_tableview, parameter, raster_formats
# from base.geodata import raster_formats
from os.path import splitext
from arcpy import FeatureToRaster_conversion

tool_settings = {"label": "Rasterise by Table",
                 "description": "Rasterise features by a 'field of fields'",
                 "can_run_background": False,
                 "category": "Feature"}


@results
@geodata
class RasteriseByTableTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterating]
        return

    @input_tableview("features_table", "Table of Features and Fields", False, ["feature:geodata:", "fields:fields:"])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterating(self):
        self.iterate_function_on_tableview(self.rasterise, "features_table", ["feature", "fields"])
        return

    def rasterise(self, data):
        feat_ds = data["feature"]

        if not self.geodata.exists(feat_ds):
            raise ValueError("'{0}' does not exist".format(feat_ds))

        if not self.geodata.is_vector(feat_ds):
            raise ValueError("'{0}' is not a feature class".format(feat_ds))

        fields_string = data["fields"]
        try:
            target_fields = [field.strip() for field in fields_string.split(",")]
        except:
            raise ValueError("Could not evaluate fields string '{0}'".format(fields_string))

        if not target_fields:
            raise ValueError("No target fields '{0}'".format(target_fields))

        for field in target_fields:
            r_out = "not set"
            try:
                r_out = self.geodata.make_raster_name("{0}_{1}".format(splitext(feat_ds)[0], field), self.results.output_workspace)
                self.send_info("Rasterising {0} on {1} -> {2}".format(feat_ds, field, r_out))
                FeatureToRaster_conversion(feat_ds, field, r_out)
                self.results.add({"geodata": r_out, "source_geodata": feat_ds, "source_field": field})
            except Exception as e:
                self.send_warning("FAILED rasterising {0} on {1}: {2}".format(feat_ds, field, str(e)))
                self.results.fail(r_out, e, data)

