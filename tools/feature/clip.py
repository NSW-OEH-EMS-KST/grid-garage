from base.base_tool import BaseTool
from base.decorators import input_output_table, input_tableview, parameter
import arcpy
import base.utils

tool_settings = {"label": "Clip",
                 "description": "Clips...",
                 "can_run_background": "True",
                 "category": "Feature"}


class ClipFeatureTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.clip_srs = None
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="feature")
    @parameter("clip_features", "Clip Features", "GPFeatureLayer", "Required", False, "Input", ["Polygon"], None, None, None,)
    @parameter("xy_tolerance", "XY Tolerance", "GPLinearUnit", "Optional", False, "Input", None, None, None, None, "Options")
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

        self.clip_srs = base.utils.get_srs(self.clip_features, raise_unknown_error=True)

        self.iterate_function_on_tableview(self.clip, return_to_results=True)

        return

    def clip(self, data):
        """

        Args:
            data:

        Returns:

        """

        fc = data["feature"]
        base.utils.validate_geodata(fc, vector=True, srs_known=True)
        fc_srs = base.utils.get_srs(fc, raise_unknown_error=True)
        base.utils.compare_srs(fc_srs, self.clip_srs, raise_no_match_error=True)

        # parse input name, construct output name
        fc_ws, fc_base, fc_name, fc_ext = base.utils.split_up_filename(fc)

        ws = self.output_file_workspace or self.output_workspace

        fc_out = base.utils.make_table_name(fc, ws, fc_ext, self.output_filename_prefix, self.output_filename_suffix)

        self.info("Clipping {0} -->> {1} ...".format(fc, fc_out))
        arcpy.Clip_analysis(fc, self.clip_features, fc_out, self.xy_tolerance)

        return {"geodata": fc_out, "source_geodata": fc}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/analysis-toolbox/clip.htm"
