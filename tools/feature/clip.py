from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview, parameter
from arcpy import Clip_analysis

tool_settings = {"label": "Clip",
                 "description": "Clips...",
                 "can_run_background": "True",
                 "category": "Feature"}


@geodata
@results
class ClipFeatureTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterating]
        self.polygons = None
        # self.point_rows = None
        self.polygons_srs = None
        # self.result_dict = {}

    @input_tableview("feature_table", "Table of Features", False, ["feature:geodata:"])
    @parameter("featureclass", "Select Polygon Feature Dataset", "DEFeatureClass", "Required", False, "Input", ["Polygon"], None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        pars = self.get_parameter_dict()
        # self.send_info(pars)

        self.polygons = pars.get("featureclass", [])

        d = self.geodata.describe(self.points)
        self.polygons_srs = d.get("dataset_spatialReference", "Unknown")
        source = d.get("general_catalogPath", None)

        if "unknown" in self.points_srs.lower():
            self.send_warning("Polygon dataset '{0}'has unknown spatial reference system ({1})".format(source, self.polygons_srs))
            exit(1)

    def iterating(self):
        self.iterate_function_on_tableview(self.process, "feature_table", ["geodata"])
        return

    def process(self, data):
        self.send_info(data)
        fc = data["feature"]
        if not self.geodata.exists(fc):
            raise ValueError("'{0}' does not exist".format(fc))
        if not self.geodata.is_featureclass(fc):
            raise ValueError("'{0}' is not a feature class".format(fc))

        d = self.geodata.describe(fc)
        # r_base = d.get("general_baseName", "None")
        fc_srs = d.get("dataset_spatialReference", "Unknown")

        if "unknown" in fc_srs.lower():
            raise ValueError("Feature class '{0}' has an unknown spatial reference system".format(fc))

        if fc_srs != self.points_srs:  # hack!! needs doing properly
            raise ValueError("Spatial reference systems do not match ({0} != {1})".format(fc_srs, self.points_srs))

        fc_out = ""  # TODO
        self.send_info("Clipping {0} -->> {1} ...".format(fc, fc_out))
        # Clip_analysis()  # TODO

        return

