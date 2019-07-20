from base.base_tool import BaseTool
from base.utils import make_vector_name, describe, get_search_cursor_rows, validate_geodata
from base.decorators import input_tableview, input_output_table, parameter
from arcpy.sa import ExtractValuesToPoints
from arcpy import MakeFeatureLayer_management, Exists, Delete_management


tool_settings = {"label": "Extract Values to Points",
                 "description": "Extracts cell values of a raster at specified points into a new feature class",
                 "can_run_background": "True",
                 "category": "Raster"}


class ExtractValuesToPointsRasterTool(BaseTool):
    """
    """
    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.point_rows = None
        self.points_srs = None
        self.result_dict = {}

        return

    @input_tableview(data_type="raster", other_fields="query query Optional query")
    @parameter("points", "Point Features", "GPFeatureLayer", "Required", False, "Input", ["Point"], None, None, None)
    @parameter("interpolate", "Interpolate Values", "GPString", "Optional", False, "Input", ["NONE", "INTERPOLATE"], None, None, None, "Options")
    @parameter("add_attributes", "Add Raster Attributes", "GPString", "Optional", False, "Input", ["VALUE_ONLY", "ALL"], None, None, None, "Options")
    @input_output_table(affixing=True)
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def initialise(self):
        """

        Returns:

        """

        d = describe(self.points, feature=True)

        self.points_srs = d.get("spatialReference", "unknown")

        source = d.get("catalogPath", None)

        if "unknown" in self.points_srs.lower():
            raise ValueError("Point dataset '{}' has unknown spatial reference system ({})".format(source, self.points_srs))

        self.point_rows = get_search_cursor_rows(self.points, ("SHAPE@XY", "OID@"))

        self.info("{} points found in '{}'".format(len(self.point_rows), self.points))

        return

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.process, return_to_results=True)

        return

    def process(self, data):
        """

        Args:
            data:

        Returns:

        """

        ras = data["raster"]
        qry = data.get("query", None)
        validate_geodata(ras, raster=True, srs_known=True)

        d = describe(ras, raster=True)
        r_base = d.get("baseName", "None")
        ras_srs = d.get("spatialReference", "Unknown")

        if ras_srs != self.points_srs:  # hack!! needs doing properly
            raise ValueError("Spatial reference systems do not match ({0} != {1})".format(ras_srs, self.points_srs))

        ws = self.output_file_workspace or self.output_workspace

        pts_out = make_vector_name(self.points, ws, "", self.output_filename_prefix, self.output_filename_suffix + "_{}".format(r_base))

        self.info("Extracting point values from {} to {}...".format(ras, pts_out))

        if qry:
            self.info("\tQuerying features '{}'".format(qry))
            if Exists("tmp"):
                Delete_management("tmp")
            MakeFeatureLayer_management(self.points, "tmp", qry)
            ExtractValuesToPoints("tmp", ras, pts_out, self.interpolate, self.add_attributes)
        else:
            ExtractValuesToPoints(self.points, ras, pts_out, self.interpolate, self.add_attributes)

        return {"geodata": pts_out, "source_points": self.points, "source_raster": ras}
