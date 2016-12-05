from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, transform_methods, raster_formats
from base.geodata import DoesNotExistError
from base.utils import split_up_filename
from arcpy import Raster
from arcpy.sa import SquareRoot, Ln

tool_settings = {"label": "Transform",
                 "description": "Transforms rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}

@results
@geodata
class TransformRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.transform = None
        self.max_stretch = None
        self.min_stretch = None
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("transform", "Method", "GPString", "Required", False, "Input", transform_methods, None, None, transform_methods[0])
    @parameter("max_stretch", "Stretch to maximum value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("min_stretch", "Stretch to minimum value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.transform = p["transform"]
        self.max_stretch = p["max_stretch"]
        self.min_stretch = p["min_stretch"]
        self.raster_format = p["raster_format"]

    def iterate(self):
        self.iterate_function_on_tableview(self.transform, "raster_table", ["raster"])
        return

    def transform(self, data):
        self.send_info(data)
        r_in = data["raster"]
        if not self.geodata.exists(r_in):
            raise DoesNotExistError(r_in)

        _, __, ras_name, ras_ext = split_up_filename(r_in)
        r_out = self.geodata.make_raster_name(r_in, self.results.output_workspace, self.raster_format)
        self.send_info("Transforming raster {0} -->> {1} using method {2}".format(r_in, r_out, self.transform))

        out_raster =None
        vals = None

        if self.transform == "Standardise":
            stdv = float(self.geodata.describe(r_in)['raster_band_stats_STD'])
            mean = float(self.geodata.describe(r_in)['raster_band_stats_MEAN'])
            vals = '{0} std={1} mean={2}'.format(self.transform, stdv, mean)
            out_raster = (Raster(r_in) - mean) / stdv

        elif self.transform == "Stretch":
            maxv = float(self.geodata.describe(r_in)['raster_band_stats_MAXIMUM'])
            minv = float(self.geodata.describe(r_in)['raster_band_stats_MINIMUM'])
            vals = '{0} old_max={1} old_min={2} new_max={3} new_min={4}'.format(
                self.transform, maxv, minv, self.max_stretch, self.min_stretch)
            # tool.info(vals)
            # tool.info(r_in)
            out_raster = ((Raster(r_in) - minv) * self.max_stretch /
                          (maxv - minv) + self.min_stretch)

        elif self.transform == "Normalise":
            maxv = float(self.geodata.describe(r_in)['raster_band_stats_MAXIMUM'])
            minv = float(self.geodata.describe(r_in)['raster_band_stats_MINIMUM'])
            vals = '{0} old_max={1} old_min={2} new_max={3} new_min={4}'.format(
                self.transform, maxv, minv, self.max_stretch, self.min_stretch)
            out_raster = (Raster(r_in) - minv) / (maxv - minv)

        elif self.transform == "Log":
            vals = '{0}'.format(self.transform)
            out_raster = Ln(r_in)

        elif self.transform == "Square-Root":
            vals = '{0}'.format(self.transform)
            out_raster = SquareRoot(r_in)

        elif self.transform == "Invert":
            maxv = float(self.geodata.describe(r_in)['MAXIMUM'])
            minv = float(self.geodata.describe(r_in)['MINIMUM'])
            vals = '{0} max={1} min={2}'.format(self.transform, maxv, minv)
            out_raster = (Raster(r_in) - (maxv + minv)) * -1

        # save and exit
        out_raster.save(r_out)
        return {"item": r_out, "metadata": "todo", "transform": vals}
