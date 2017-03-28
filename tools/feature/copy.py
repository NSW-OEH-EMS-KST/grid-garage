import base.base_tool
import base.results
from base.method_decorators import input_output_table_with_output_affixes, input_tableview, parameter
from os.path import splitext
import base.utils
import arcpy


tool_settings = {"label": "Copy",
                 "description": "Copies...",
                 "can_run_background": "True",
                 "category": "Feature"}


@base.results.result
class CopyFeatureTool(base.base_tool.BaseTool):

    def __init__(self):
        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("features_table", "Table for Features", False, ["feature:geodata:"])
    @parameter("config_kw", "Config Keyword", "GPString", "Optional", False, "Input", None, "configKeyword", None, None)
    @parameter("sg_1", "Spatial Grid 1", "GPDouble", "Optional", False, "Input", None, None, None, 0, "Options")
    @parameter("sg_2", "Spatial Grid 2", "GPDouble", "Optional", False, "Input", None, None, None, 0, "Options")
    @parameter("sg_3", "Spatial Grid 3", "GPDouble", "Optional", False, "Input", None, None, None, 0, "Options")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    # def initialise(self):
    # #     p = self.get_parameter_dict()
    # #     self.config_kw = p["config_kw"]if p["config_kw"] else "#"
    # #     self.sg_1 = p["sg_1"] if p["sg_1"] else 0
    # #     self.sg_2 = p["sg_2"] if p["sg_2"] else 0
    # #     self.sg_3 = p["sg_3"] if p["sg_2"] else 0
    #     return

    def iterate(self):

        self.iterate_function_on_tableview(self.process, "features_table", ["feature"])

        return

    def process(self, data):

        fc = data["feature"]
        self.geodata.validate_geodata(fc, vector=True)

        ws = self.results.output_workspace
        ex = splitext(fc)[1]
        nfc = base.utils.make_vector_name(fc, ws, ex)

        self.log.info('copying {0} --> {1}'.format(fc, nfc))
        # CopyFeatures_management(in_features, out_feature_class, {config_keyword}, {spatial_grid_1}, {spatial_grid_2}, {spatial_grid_3})
        arcpy.CopyFeatures_management(fc, nfc, self.config_kw, self.sg_1, self.sg_2, self.sg_3)

        self.result.add({'geodata': nfc, 'copied_from': fc})

        return

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy-features.htm"
# "CopyFeatures_management (in_features, out_feature_class, {config_keyword}, {spatial_grid_1}, {spatial_grid_2}, {spatial_grid_3})"