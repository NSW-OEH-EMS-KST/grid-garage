from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats
import arcpy

tool_settings = {"label": "Tweak Values",
                 "description": "Tweaks raster cell values with simple mathematics and can integerise result",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class TweakValuesRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
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

        return BaseTool.getParameterInfo(self)

    def initialise(self):

        if not (self.min_val or self.max_val or self.constant or self.scalar or self.integerise):
            raise ValueError("No tweaks specified")

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.tweak, "raster_table", ["geodata"], return_to_results=True)

        return

    def tweak(self, data):

        r_in = data["geodata"]
        utils.validate_geodata(r_in, raster=True)

        r_out = utils.make_raster_name(r_in, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        ras = arcpy.Raster(r_in)
        ndv = ras.noDataValue
        pix_type = ras.pixelType
        if any(x in pix_type for x in ["S", "U"]):
            self.info("Raster pixel type is '{}' (integer)".format(pix_type))
            try:
                ndv = int(ndv)
            except:
                pass
            try:
                self.min_val = int(self.min_val)
            except:
                pass
            try:
                self.max_val = int(self.max_val)
            except:
                pass

        self.info(["Tweaking raster {}".format(r_in), "\tNoData Value is {}".format(ndv)])

        tweaks = []

        if self.scalar:
            self.info('\tScaling by {}'.format(self.scalar))
            ras *= float(self.scalar)
            tweaks.append('scaled by {}'.format(self.scalar))

        if self.constant:
            self.info('\tTranslating by {}'.format(self.constant))
            ras += float(self.constant)
            tweaks.append('translated by {}'.format(self.constant))

        if self.min_val:
            self.info('\tSetting minimum to {} values under will go to {}'.format(self.min_val, self.under_min))
            under = self.min_val if self.under_min == 'Minimum' else ndv
            if under == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            ras = arcpy.sa.Con(ras >= self.min_val, ras, under)
            tweaks.append('Minimum set to {} under set to {}'.format(self.min_val, under))

        if self.max_val:
            self.info('\tSetting maximum to {} values over will go to {}'.format(self.max_val, self.over_max))
            over = self.max_val if self.over_max == 'Maximum' else ndv
            if over == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            ras = arcpy.sa.Con(ras <= self.max_val, ras, over)
            tweaks.append('Maximum set to {} over set to {}'.format(self.max_val, over))

        if self.integerise:
            self.info('\tIntegerising...')
            ras = arcpy.sa.Int(ras)
            tweaks.append('integerised (truncation)')

        # save and exit
        self.info('\tSaving to {}'.format(r_out))
        ras.save(r_out)

        return {"geodata": r_out, "source_geodata": r_in, "tweaks": ' & '.join(tweaks)}

# Con (in_conditional_raster, in_true_raster_or_constant, {in_false_raster_or_constant}, {where_clause})
