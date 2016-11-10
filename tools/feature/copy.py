from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview, parameter
from os.path import splitext

tool_settings = {"label": "Copy",
                 "description": "Copies...",
                 "can_run_background": "True",
                 "category": "Feature"}


@geodata
@results
class CopyFeatureTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.config_kw = None
        self.sg_1 = None
        self.sg_2 = None
        self.sg_3 = None

    @input_tableview("features_table", "Table for Features", False, ["feature:geodata:"])
    @parameter("config_kw", "Config Keyword", "GPString", "Optional", False, "Input", None, "configKeyword", None, None)
    @parameter("sg_1", "Spatial Grid 1", "GPDouble", "Optional", False, "Input", None, None, None, 0)
    @parameter("sg_2", "Spatial Grid 2", "GPDouble", "Optional", False, "Input", None, None, None, 0)
    @parameter("sg_3", "Spatial Grid 3", "GPDouble", "Optional", False, "Input", None, None, None, 0)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.config_kw = p["config_kw"]if p["config_kw"] else "#"
        self.sg_1 = p["sg_1"] if p["sg_1"] else 0
        self.sg_2 = p["sg_2"] if p["sg_2"] else 0
        self.sg_3 = p["sg_3"] if p["sg_2"] else 0

    def iterate(self):
        self.iterate_function_on_tableview(self.process, "features_table", ["feature"])
        return

    def process(self, data):
        fc = data["feature"]
        self.geodata.validate_geodata(fc, vector=True)

        ws = self.results.output_workspace
        ex = splitext(fc)[1]
        nfc = self.geodata.make_vector_name(fc, ws, ex)

        self.send_info('copying {0} --> {1}'.format(fc, nfc))
        # CopyFeatures_management(in_features, out_feature_class, {config_keyword}, {spatial_grid_1}, {spatial_grid_2}, {spatial_grid_3})
        self.geodata.copy_feature(fc, nfc, self.config_kw, self.sg_1, self.sg_2, self.sg_3)

        self.results.add({'geodata': nfc, 'copied_from': fc})
        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy-features.htm"