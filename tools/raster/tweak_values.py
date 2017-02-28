from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, raster_formats
from base.geodata import DoesNotExistError
from arcpy import Raster, Describe
from arcpy.sa import Con, Int
from os.path import join

tool_settings = {"label": "Tweak Values",
                 "description": "Tweaks...",
                 "can_run_background": "True",
                 "category": "Raster"}

@results
@geodata
class TweakValuesRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.min_val = None
        self.under_min = None
        self.max_val = None
        self.over_max = None
        self.scalar = None
        self.constant = None
        self.integerise = None
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("min_val", "Minimum value", "GPDouble", "Optional", False, "Input", None, None, None, None)
    @parameter("under_min", "Values < Minumium", "GPString", "Optional", False, "Input", ["Minimum", "NoData"], None, None, "Minimum")
    @parameter("max_val", "Maximum value", "GPDouble", "Optional", False, "Input", None, None, None, None)
    @parameter("over_max", "Values > Maxumium", "GPString", "Optional", False, "Input", ["Maximum", "NoData"], None, None, "Maximum")
    @parameter("scaler", "Scale Factor", "GPDouble", "Optional", False, "Input", None, None, None, None)
    @parameter("constant", "Constant Shift", "GPDouble", "Optional", False, "Input", None, None, None, None)
    @parameter("integerise", "integerise", "GPBoolean", "Optional", False, "Input", None, None, None, False)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.min_val = p["min_val"]
        self.under_min = p["under_min"]
        self.max_val = p["max_val"]
        self.over_max = p["over_max"]
        self.scalar = p["scaler"]
        self.constant = p["constant"]
        self.integerise = p["integerise"]
        self.raster_format = p["raster_format"]
        if not (self.min_val or self.max_val or self.constant or self.scalar or self.integerise):
            raise ValueError("No tweaks specified")

    def iterate(self):
        self.iterate_function_on_tableview(self.tweak, "raster_table", ["raster"])
        return

    def get_band_nodata(self, raster, bandindex=1):
        d = Describe(join(raster, "Band_{}".format(bandindex)))
        ndv = d.noDataValue
        # v = ap.GetRasterProperties_management(raster, property)
        # self.send_info(type(v))
        # v = v.getOutput(0)
        # print type(v)
        return ndv

    def tweak(self, data):
        r_in = data["raster"]
        if not self.geodata.exists(r_in):
            raise DoesNotExistError(r_in)

        r_out = self.geodata.make_raster_name(r_in, self.results.output_workspace, self.raster_format)
        self.send_info("Tweaking raster {0} -->> {1}".format(r_in, r_out))

        ras = Raster(r_in)
        vals = []

        if self.min_val:
            self.send_info('Setting minimum {0}...{1}'.format(self.min_val, self.under_min))
            under = self.min_val if self.under_min == 'Minimum' else self.get_band_nodata(r_in)  # self.geodata.describe(r_in)["raster_band_noDataValue"]
            # self.send_info(under)
            if under == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            # self.send_info(under)
            ras = Con(ras >= float(self.min_val), ras, float(under))
            vals.append('MIN {0}...{1} = {2}'.format(self.min_val, self.under_min, under))

        if self.max_val:
            self.send_info('Setting maximum {0}...{1}'.format(self.max_val, self.over_max))
            over = self.max_val if self.over_max == 'Maximum' else self.get_band_nodata(r_in)  # self.geodata.describe(r_in)["raster_band_noDataValue"]
            # self.send_info(over)
            if over == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
                # over = None
            # self.send_info(over)
            ras = Con(ras <= float(self.max_val), ras, float(over))
            vals.append('MAX {0}...{1}'.format(self.max_val, self.over_max, over))

        if self.scalar:
            self.send_info('Scaling...{0}'.format(self.scalar))
            ras *= float(self.scalar)
            vals.append('scaled by {0}'.format(self.scalar))

        if self.constant:
            self.send_info('Translating...{0}'.format(self.constant))
            ras += float(self.constant)
            vals.append('translated by {0}'.format(self.constant))

        if self.integerise:
            self.send_info('Integerising...')
            ras = Int(ras)
            vals.append('integerised (truncation)')

        # save and exit
        self.send_info('Saving to {0}'.format(r_out))
        ras.save(r_out)

        self.results.add({"geodata": r_out, "source_geodata": r_in, "tweaks": ' & '.join(vals)})
        return

# Con (in_conditional_raster, in_true_raster_or_constant, {in_false_raster_or_constant}, {where_clause})


