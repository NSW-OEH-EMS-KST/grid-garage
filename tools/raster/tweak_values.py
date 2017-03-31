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
        # self.min_val = None
        # self.under_min = None
        # self.max_val = None
        # self.over_max = None
        # self.scalar = None
        # self.constant = None
        # self.integerise = None
        # self.raster_format = None

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("min_val", "Minimum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("under_min", "Values < Minumium", "GPString", "Optional", False, "Input", ["Minimum", "NoData"], None, None, "Minimum", "Options")
    @parameter("max_val", "Maximum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("over_max", "Values > Maxumium", "GPString", "Optional", False, "Input", ["Maximum", "NoData"], None, None, "Maximum", "Options")
    @parameter("scaler", "Scale Factor", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("constant", "Constant Shift", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("integerise", "integerise", "GPBoolean", "Optional", False, "Input", None, None, None, False, "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def initialise(self):
        # p = self.get_parameter_dict()
        # self.min_val = p["min_val"]
        # self.under_min = p["under_min"]
        # self.max_val = p["max_val"]
        # self.over_max = p["over_max"]
        # self.scalar = p["scaler"]
        # self.constant = p["constant"]
        # self.integerise = p["integerise"]
        # self.raster_format = p["raster_format"]
        if not (self.min_val or self.max_val or self.constant or self.scalar or self.integerise):
            raise ValueError("No tweaks specified")

    def iterate(self):

        self.iterate_function_on_tableview(self.tweak, "raster_table", ["raster"])

        return

    def tweak(self, data):

        r_in = data["raster"]
        base.utils.validate_geodata(r_in, raster=True)

        r_out = base.utils.make_raster_name(r_in, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
        self.log.info("Tweaking raster {0} -->> {1}".format(r_in, r_out))

        ras = arcpy.Raster(r_in)
        vals = []

        if self.min_val:
            self.log.info('Setting minimum {0}...{1}'.format(self.min_val, self.under_min))
            under = self.min_val if self.under_min == 'Minimum' else base.utils.get_band_nodata(r_in)  # self.geodata.describe(r_in)["raster_band_noDataValue"]
            # self.send_info(under)
            if under == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            # self.send_info(under)
            ras = arcpy.sa.Con(ras >= float(self.min_val), ras, float(under))
            vals.append('MIN {0}...{1} = {2}'.format(self.min_val, self.under_min, under))

        if self.max_val:
            self.log.info('Setting maximum {0}...{1}'.format(self.max_val, self.over_max))
            over = self.max_val if self.over_max == 'Maximum' else base.utils.get_band_nodata(r_in)  # self.geodata.describe(r_in)["raster_band_noDataValue"]
            # self.send_info(over)
            if over == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
                # over = None
            # self.send_info(over)
            ras = arcpy.sa.Con(ras <= float(self.max_val), ras, float(over))
            vals.append('MAX {0}...{1}'.format(self.max_val, self.over_max, over))

        if self.scalar:
            self.log.info('Scaling...{0}'.format(self.scalar))
            ras *= float(self.scalar)
            vals.append('scaled by {0}'.format(self.scalar))

        if self.constant:
            self.log.info('Translating...{0}'.format(self.constant))
            ras += float(self.constant)
            vals.append('translated by {0}'.format(self.constant))

        if self.integerise:
            self.log.info('Integerising...')
            ras = arcpy.sa.Int(ras)
            vals.append('integerised (truncation)')

        # save and exit
        self.log.info('Saving to {0}'.format(r_out))
        ras.save(r_out)

        r = self.result.add({"geodata": r_out, "source_geodata": r_in, "tweaks": ' & '.join(vals)})
        self.log.info(r)

        return

# Con (in_conditional_raster, in_true_raster_or_constant, {in_false_raster_or_constant}, {where_clause})
