
from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview, parameter
from arcpy import Clip_analysis
from base.utils import split_up_filename, join_up_filename

tool_settings = {"label": "Clip",
                 "description": "Clips...",
                 "can_run_background": "True",
                 "category": "Feature"}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/analysis-toolbox/clip.htm"
@geodata
@results
class ClipFeatureTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.clip_features = None
        self.clip_srs = None
        self.xy_tolerance = None
        self.meta = None
        self.execution_list = [self.initialise, self.iterating]

    @input_tableview("feature_table", "Table of Features", False, ["feature:geodata:"])
    @parameter("clip_features", "Clip Features", "DEFeatureClass", "Required", False, "Input", ["Polygon"], None, None, None)
    @parameter("xy_tolerance", "XY Tolerance", "GPLinearUnit", "Optional", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        pars = self.get_parameter_dict()
        self.clip_features = pars["clip_features"]
        self.clip_srs = self.geodata.get_srs(geodata, raise_unknown_error=True)
        self.xy_tolerance = pars["xy_tolerance"] if pars["xy_tolerance"] else "#"

    def iterating(self):
        self.iterate_function_on_tableview(self.process, "feature_table", ["geodata"])
        return

    def process(self, data):
        # self.send_info(data)
        fc = data["feature"]
        self.geodata.validate_geodata(fc, vector=True)
        fc_srs = self.geodata.get_srs(fc, raise_unknown_error=True)
        self.geodata.compare_srs(fc_srs, self.clip_srs, raise_no_match_error=True)

        # parse input name, construct output name
        fc_ws, fc_base, fc_name, fc_ext = split_up_filename(fc)
        fc_out = join_up_filename(self.output_workspace, fc_name, ('shp', '')[self.output_workspace_type == "LocalDatabase"])

        self.send_info("Clipping {0} -->> {1} ...".format(fc, fc_out))
        Clip_analysis(fc, self.clip_features, fc_out, self.xy_tolerance)

        self.results.add({"geodata": fc_out, "source_geodata": fc})
        return

