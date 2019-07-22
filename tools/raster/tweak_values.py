from base.base_tool import BaseTool
from base import utils
from base.decorators import input_tableview, input_output_table, parameter, raster_formats
import arcpy
from arcpy.sa import *

tool_settings = {"label": "Tweak Values",
                 "description": "Tweaks raster cell values with simple mathematics and can integerise result",
                 "can_run_background": "True",
                 "category": "Raster"}


class TweakValuesRasterTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @input_tableview(data_type="raster")
    @parameter("scalar", "Scale Factor", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("constant", "Constant Shift", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("min_val", "Minimum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("under_min", "Values Under Minimum", "GPString", "Optional", False, "Input", ["Minimum", "NoData"], None, None, "Minimum", "Options")
    @parameter("max_val", "Maximum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("over_max", "Values Over Maximum", "GPString", "Optional", False, "Input", ["Maximum", "NoData"], None, None, "Maximum", "Options")
    @parameter("integerise", "Integerise Result", "GPBoolean", "Optional", False, "Input", None, None, None, False, "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
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

        if not (self.min_val or self.max_val or self.constant or self.scalar or self.integerise):
            raise ValueError("No tweaks specified")

        return

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.tweak, return_to_results=True)

        return

    def tweak(self, data):
        """

        Args:
            data:

        Returns:

        """

        r_in = data["raster"]
        utils.validate_geodata(r_in, raster=True)

        ws = self.output_file_workspace or self.output_workspace

        r_out = utils.make_raster_name(r_in, ws, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        ras = Raster(r_in)
        ndv = ras.noDataValue
        pix_type = ras.pixelType
        if any(x in pix_type for x in ["S", "U"]):
            self.info("Raster pixel type is '{}' (integer)".format(pix_type))
            try:
                ndv = int(ndv)
            except:
                self.info("ndv could not be coerced to integer, ndv is {}".format(ndv))
                pass
            try:
                self.min_val = int(self.min_val)
            except:
                self.info("minimum value could not be coerced to integer, min_val is {}".format(self.min_val))
                pass
            try:
                self.max_val = int(self.max_val)
            except:
                self.info("maximum value could not be coerced to integer, max_val is {}".format(self.max_val))
                pass

        self.info("Tweaking raster {}, \tNoData Value is {}".format(r_in, ndv))

        tweaks = []

        if self.scalar:
            self.info('\tScaling by {}'.format(self.scalar))
            ras *= self.scalar
            tweaks.append('scaled by {}'.format(self.scalar))

        if self.constant:
            self.info('\tTranslating by {}'.format(self.constant))
            ras += self.constant
            tweaks.append('translated by {}'.format(self.constant))

        if self.min_val or (self.min_val == 0):
            self.info('\tSetting minimum to {}  any values below this will reset'.format(self.min_val))
            under = self.min_val if self.under_min == 'Minimum' else ndv
            if under == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            ras = arcpy.sa.Con(ras < self.min_val, under, ras)
            tweaks.append('Minimum set to {}'.format(self.min_val))

        if self.max_val or (self.max_val == 0):
            self.info('\tSetting maximum to {} any values above this will be reset'.format(self.max_val))
            over = self.max_val if self.over_max == 'Maximum' else ndv
            if over == "#":
                raise ValueError("Raster '{}' does not have a nodata value".format(r_in))
            ras = arcpy.sa.Con(ras > self.max_val, over, ras)
            tweaks.append('Maximum set to {}'.format(self.max_val))

        if self.integerise:
            self.info('\tIntegerising...')
            ras = arcpy.sa.Int(ras)
            tweaks.append('integerised (truncation)')

        # save and exit
        self.info('\tSaving to {}'.format(r_out))
        ras.save(r_out)
        arcpy.SetRasterProperties_management(in_raster=r_out, nodata=[[1, ndv]])

        return {"raster": r_out, "source_geodata": r_in, "tweaks": ' & '.join(tweaks)}

# Con (in_conditional_raster, in_true_raster_or_constant, {in_false_raster_or_constant}, {where_clause})
