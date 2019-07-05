from base.base_tool import BaseTool
from base.decorators import input_output_table, input_tableview, parameter
from os.path import splitext
from arcpy import TabulateIntersection_analysis

import base.utils


tool_settings = {"label": "Tabulate Intersection",
                 "description": "Compute the intersection between two feature classes and cross-tabulates the area, length, or count of the intersecting features.",
                 "can_run_background": "True",
                 "category": "Feature"}


class TabulateIntersectionTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="feature", other_fields="zone_fields Zone_Fields Required zone_fields")
    # @input_tableview(data_type="classes", ob_name="in_class_table", ob_title="Classes Table", other_fields="class_feature_field Class_Feature Required class_feature_field, classes_fields Classes_Fields Required classes_field, sum_fields Sum_Fields Required sum_fields")
    @input_tableview(ob_name="Class Features", other_fields="class_feature_field Class_Feature Required class_feature_field, classes_fields Classes_Fields Required classes_field, sum_fields Sum_Fields Required sum_fields")
    @parameter("xy_tol", "XY Tolerance", "GPLinearUnit", "Optional", False, "Input", None, None, None, None, None)
    @parameter("out_unit", "Output Units", "GPString", "Optional", False, "Input", ["unit1", "unit2"], None, None, None, None)
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

        self.iterate_function_on_tableview(self.tabulate)

        return

# TabulateIntersection_analysis(in_zone_features, zone_fields, in_class_features, out_table, {class_fields},
#                               {sum_fields}, {xy_tolerance}, {out_units})

    def tabulate(self, data):
        """

        Args:
            data:
        """

        feat_ds = data["feature"]
        base.utils.validate_geodata(feat_ds, vector=True)

        fields_string = data["table_fields"]
        try:
            target_fields = [field.strip() for field in fields_string.split(",")]
        except:
            raise ValueError("Could not evaluate fields string '{0}'".format(fields_string))

        if not target_fields:
            raise ValueError("No target fields '{0}'".format(target_fields))

        for field in target_fields:
            try:
                r_out = base.utils.make_raster_name("{0}_{1}".format(splitext(feat_ds)[0], field), self.output_file_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
                self.info("Rasterising {0} on {1} -> {2}".format(feat_ds, field, r_out))
                FeatureToRaster_conversion(feat_ds, field, r_out)
                self.result.add_pass({"geodata": r_out, "source_geodata": feat_ds, "source_field": field})
            except Exception as e:
                self.error("FAILED rasterising {0} on {1}: {2}".format(feat_ds, field, str(e)))
                self.result.add_fail(data)

#   FeatureToRaster_conversion (in_features, field, out_raster, {cell_size})
