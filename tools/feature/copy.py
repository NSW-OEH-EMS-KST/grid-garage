import base.base_tool
from base.decorators import input_output_table, input_tableview, parameter
from os.path import splitext
import base.utils
import arcpy


tool_settings = {"label": "Copy",
                 "description": "Copies...",
                 "can_run_background": "True",
                 "category": "Feature"}


class CopyFeatureTool(base.base_tool.BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """
        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="feature")
    @parameter("config_kw", "Config Keyword", "GPString", "Optional", False, "Input", None, "configKeyword", None, None)
    @parameter("sg_1", "Spatial Grid 1", "GPLong", "Optional", False, "Input", None, None, None, 0, "Options")
    @parameter("sg_2", "Spatial Grid 2", "GPLong", "Optional", False, "Input", None, None, None, 0, "Options")
    @parameter("sg_3", "Spatial Grid 3", "GPLong", "Optional", False, "Input", None, None, None, 0, "Options")
    @input_output_table(affixing=True)
    def getParameterInfo(self):
        """

        Returns:

        """

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        # self.iterate_function_on_tableview(self.process, "features_table", ["geodata"], return_to_results=True)
        self.iterate_function_on_tableview(self.process, return_to_results=True)

        return

    def process(self, data):
        """

        Args:
            data:

        Returns:

        """

        fc = data["geodata"]
        base.utils.validate_geodata(fc, vector=True)

        ws = self.result.output_workspace
        ex = splitext(fc)[1]

        nfc = base.utils.make_vector_name(fc, ws, ex, self.output_filename_prefix, self. output_filename_suffix)

        self.info('copying {0} --> {1}'.format(fc, nfc))
        arcpy.CopyFeatures_management(fc, nfc, self.config_kw, self.sg_1, self.sg_2, self.sg_3)

        return {'geodata': nfc, 'copied_from': fc}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy-features.htm"
# "CopyFeatures_management (in_features, out_feature_class, {config_keyword}, {spatial_grid_1}, {spatial_grid_2}, {spatial_grid_3})"
