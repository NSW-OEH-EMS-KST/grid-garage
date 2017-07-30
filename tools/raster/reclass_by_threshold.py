from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, data_nodata, raster_formats
import arcpy
from collections import OrderedDict


tool_settings = {"label": "Reclass by Threshold",
                 "description": "Reclass by threshold values found in fields...",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class ReclassByThresholdRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["thresholds:thresholds:", "raster:geodata:"])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        try:
            self.info(self.thresholds)
        except:
            pass
        self.iterate_function_on_tableview(self.reclass, "raster_table", ["geodata", "thresholds"], return_to_results=True)

        return

    def make_remap(self, value, minv, maxv):
        self.info(locals())

        if not value:
            raise ValueError("No threshold string")

        thresholds = value.split(",")

        if not thresholds:
            raise ValueError("\tNo thresholds set")

        thresholds = sorted([float(t.strip()) for t in thresholds])
        # thresholds = sorted(thresholds + [minv, maxv])
        self.info("sorted thresholds are {}".format(thresholds))
        # thresholds = [(t, t + 0.0001, i) for i, t in enumerate(thresholds, start=1)]
        # # thresholds = [(t, t + 0.0001, i) for i, t in enumerate(thresholds, start=1)]
        # self.info("endpoint thresholds are {}".format(thresholds))
        # thresholds = sorted(thresholds + [minv, maxv])
        # self.info("endpoint thresholds LIST are {}".format(thresholds))

        mint, maxt = min(thresholds), max(thresholds)

        if mint < minv:
            raise ValueError("\tMin threshold under min value {} < {}".format(mint, minv))
        if maxt > maxv:
            raise ValueError("\tMax threshold over max value {} > {}".format(maxt, maxv))

        # thresholds = [(t, t + 0.0001, i) for i, t in enumerate(thresholds, start=1)]
        # thresholds = [item for t in thresholds for item in t]

        # v = [min] + thresholds + [max]
        # thresholds = ["{} {} {}".format((t, t + 1)
        # flat_list = [item for sublist in l for item in sublist]
        # 93, 134
        # 93, 94, 134, 135
        # 0, 93 , 134, 1000
        # thresholds2 = [(v, v + 0.0001) for v in thresholds]
        # self.info(thresholds2)
        #
        # thresholds2 = [minv] + thresholds2 + [maxv]
        # self.info(thresholds2)
        delta = 0.0001
        thresholds2 = [(minv, thresholds[0], 1), (thresholds[len(thresholds)-1], maxv, thresholds[len(thresholds)-1])]
        # for t in thresholds:
        for i, t in enumerate(thresholds):
            thresholds2.append("{} {} {}".format(from_v, to_v, i + 1))
            # if i == 0:
            #     from_v = minv
            # else:
            #     from_v = thresholds[i-1] + delta
            #
            # if i == (len(thresholds)+1):
            #     to_v = maxv
            # else:
            #     to_v = thresholds[i]

            thresholds2.append("{} {} {}".format(from_v, to_v, i + 1))
        # thresholds2 = []
        # for t in thresholds:
        #     thresholds2.append(t)
        #     thresholds2.append(t+1)
        self.info(thresholds2)
        remap = ";".join(thresholds2)
        self.info(remap)
        return thresholds

    def reclass(self, data):

        parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in self.parameters])
        parameter_summary = ", ".join(["{}: {}".format(k, v) for k, v in parameter_dictionary.iteritems()])
        self.info("Parameter summary: {}".format(parameter_summary))

        self.info("data : {}".format(data))
        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)

        ras_out = utils.make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self. output_filename_suffix)

        self.info("Reclassifying {} -->> {}...".format(ras, ras_out))

        remap = data["thresholds"]
        if not remap:
            raise ValueError("\tNo thresholds set")

        self.info("\tUpdating RAT...")
        arcpy.BuildRasterAttributeTable_management(ras, "Overwrite")

        self.info("\tUpdating statistics...")
        arcpy.CalculateStatistics_management(ras)

        # "0 5 1;5.01 7.5 2;7.5 10 3"  from, to, new
        minv = float(arcpy.GetRasterProperties_management(ras, "MINIMUM").getOutput(0))
        maxv = float(arcpy.GetRasterProperties_management(ras, "MAXIMUM").getOutput(0))
        mean = float(arcpy.GetRasterProperties_management(ras, "MEAN").getOutput(0))
        std = float(arcpy.GetRasterProperties_management(ras, "STD").getOutput(0))

        # remap = self.make_remap(data["thresholds"], minv, maxv)
        remap = remap.replace("MIN", str(minv)).replace("MAX", str(maxv))

        self.info([ras, "Value", remap, ras_out, "NODATA"])
        arcpy.Reclassify_3d(ras, "Value", remap, ras_out, "NODATA")

        # AddField_management(in_table, field_name, field_type, {field_precision}, {field_scale}, {field_length}, {field_alias}, {field_is_nullable},
        #                     {field_is_required}, {field_domain})
        arcpy.AddField_management(ras_out, "asdst_value", "TEXT")

        v = ["no", "Low", "Medium", "High"]
        with arcpy.da.UpdateCursor(ras_out, ["asdst_value", "Value"]) as cursor:
            for row in cursor:
                row[0] = v[row[1]]
                cursor.updateRow(row)

                # arcpy.Reclassify_3d("C:/data/landuse", "VALUE",
    #                     "1 9;2 8;3 1;4 6;5 3;6 2;7 1",
    #                     "C:/output/outremap", "DATA")

        return {"geodata": ras_out, "source_geodata": ras, "min_max_mean_std": "{}_{}_{}_{}".format(minv, maxv, mean, std), "remap": remap}

