import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table, parameter
from arcpy import GetCellValue_management
from collections import OrderedDict
import base.utils

tool_settings = {"label": "Values at Points",
                 "description": "Retrieves the values of rasters at specified points...",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class ValuesAtPointsRasterTool(base.base_tool.BaseTool):
    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterating, self.finish]
        self.point_rows = None
        self.points_srs = None
        self.result_dict = {}

        return

    @input_tableview("raster_table", "Table of Rasters", False, ["raster:geodata:"])
    @parameter("points", "Point Features", "GPFeatureLayer", "Required", False, "Input", ["Point"], None, None, None)
    @input_output_table
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def initialise(self):

        d = base.utils.describe(self.points)
        self.points_srs = d.get("dataset_spatialReference", "Unknown")
        source = d.get("general_catalogPath", None)

        if "unknown" in self.points_srs.lower():
            raise ValueError("Point dataset '{0}'has unknown spatial reference system ({1})".format(source, self.points_srs))

        self.point_rows = self.geodata.get_search_cursor_rows(self.points, ("SHAPE@XY", "OID@"))
        self.log.info("{0} points found in '{1}'".format(len(self.point_rows), self.points))

        return

    def iterating(self):

        self.iterate_function_on_tableview(self.process, "raster_table", ["raster"])

        return

    def process(self, data):

        ras = data["raster"]
        base.utils.validate_geodata(ras, raster=True, srs_known=True)

        d = base.utils.describe(ras)
        r_base = d.get("general_baseName", "None")
        ras_srs = d.get("dataset_spatialReference", "Unknown")

        if ras_srs != self.points_srs:  # hack!! needs doing properly
            raise ValueError("Spatial reference systems do not match ({0} != {1})".format(ras_srs, self.points_srs))

        self.log.info("Extracting point values from {0}...".format(ras))

        for row in self.point_rows:
            oid = row[1]
            # calc
            xy = "{0} {1}".format(row[0][0], row[0][1])
            result = GetCellValue_management(ras, xy)
            val = result.getOutput(0)
            # get the storage
            id_res = self.result_dict.get(oid, None)
            if not id_res:  # init needed
                id_res = {}
                self.result_dict[oid] = id_res
            # store it
            id_res[r_base] = val

        # Get the Band_2 and Band_3 cell value of certain point in a RGB image
        # result = arcpy.GetCellValue_management("rgb.img", "480785 3807335", "2;3")
        # cellSize = int(result.getOutput(0)) TODO
        #
        # individual results are being accumulated not added on by one
        # as they are nested and need unravelling... see below ::finish()
        return

    def finish(self):

        result_list = []

        for oid, val_dict in self.result_dict.iteritems():
            # row_dict = {"source_pt_id": oid}
            row_dict = OrderedDict()
            row_dict["source_pt_id"] = oid
            for k, v in val_dict.iteritems():
                row_dict[k] = v
            result_list.append(row_dict)

        self.results.add(result_list)

        return
