import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats
import arcpy
import base.utils

tool_settings = {"label": "Tweak Values",
                 "description": "Tweaks raster cell values with simple mathematics and can integerise result",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class TweakValuesRasterTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("scalar", "Scale Factor", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("constant", "Constant Shift", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("min_val", "Minimum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("under_min", "Values Under Minumium", "GPString", "Optional", False, "Input", ["Minimum", "NoData"], None, None, "Minimum", "Options")
    @parameter("max_val", "Maximum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("over_max", "Values Over Maximum", "GPString", "Optional", False, "Input", ["Maximum", "NoData"], None, None, "Maximum", "Options")
    @parameter("integerise", "Integerise Result", "GPBoolean", "Optional", False, "Input", None, None, None, False, "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def initialise(self):

        if set([self.min_val, self.max_val, self.constant, self.scalar]) == ["#"] and not self.integerise:
            raise ValueError("No tweaks specified")

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.tweak, "raster_table", ["raster"])

        return

    def tweak(self, data):

        r_in = data["raster"]
        base.utils.validate_geodata(r_in, raster=True)

        r_out = base.utils.make_raster_name(r_in, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
        self.log.info("Tweaking raster {}".format(r_in))

        ras = arcpy.Raster(r_in)
        tweaks = []
        ndv = base.utils.get_band_nodata_value(r_in)

        if self.scalar != "#":
            self.log.info('\tScaling by {}'.format(self.scalar))
            ras *= float(self.scalar)
            tweaks.append('scaled by {}'.format(self.scalar))

        if self.constant != "#":
            self.log.info('\tTranslating by {}'.format(self.constant))
            ras += float(self.constant)
            tweaks.append('translated by {}'.format(self.constant))

        if self.min_val != "#":
            self.log.info('\tSetting minimum to {} values under will go to {}'.format(self.min_val, self.under_min))
            under = self.min_val if self.under_min == 'Minimum' else ndv
            if under == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            ras = arcpy.sa.Con(ras >= float(self.min_val), ras, float(under))
            tweaks.append('Minimum set to {} under set to {}'.format(self.min_val, under))

        if self.max_val != "#":
            self.log.info('\tSetting maximum to {} values over will go to {}'.format(self.max_val, self.over_max))
            over = self.max_val if self.over_max == 'Maximum' else ndv
            if over == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            ras = arcpy.sa.Con(ras <= float(self.max_val), ras, float(over))
            tweaks.append('Maximum set to {} over set to {}'.format(self.max_val, over))

        if self.integerise != "#":
            self.log.info('\tIntegerising...')
            ras = arcpy.sa.Int(ras)
            tweaks.append('integerised (truncation)')

        # save and exit
        self.log.info('\tSaving to {}'.format(r_out))
        ras.save(r_out)

        r = self.result.add({"geodata": r_out, "source_geodata": r_in, "tweaks": ' & '.join(tweaks)})
        self.log.info(r)

        return

# Con (in_conditional_raster, in_true_raster_or_constant, {in_false_raster_or_constant}, {where_clause})
