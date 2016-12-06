from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, transform_methods, raster_formats
from base.geodata import DoesNotExistError
from base.utils import split_up_filename
import arcpy
import numpy as np

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
        self.method = None
        self.max_stretch = None
        self.min_stretch = None
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("method", "Method", "GPString", "Required", False, "Input", transform_methods, None, None, transform_methods[0])
    @parameter("max_stretch", "Stretch to maximum value", "GPDouble", "Optional", False, "Input", None, None, None, None)
    @parameter("min_stretch", "Stretch to minimum value", "GPDouble", "Optional", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def updateParameters(self, parameters):
        BaseTool.updateParameters(self, parameters)
        parameters[3].enabled = parameters[4].enabled = parameters[2].value == 'STRETCH'
        return

    def updateMessages(self, parameters):
        BaseTool.updateMessages(self, parameters)
        stretch = parameters[2].value == 'STRETCH'
        if stretch and not parameters[3].valueAsText:
            parameters[3].setIDMessage("ERROR", 735, parameters[3].displayName)
        if stretch and not parameters[4].valueAsText:
            parameters[4].setIDMessage("ERROR", 735, parameters[4].displayName)
        return

    def initialise(self):
        p = self.get_parameter_dict()
        self.send_info(p)
        self.method = p["method"]
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

        self.send_info("Transforming raster {0} -->> {1} using method {2}".format(r_in, r_out, self.method))
        nd_out = None
        vals = None

        self.send_info("...reading raster array...")
        nd_in = arcpy.RasterToNumPyArray(r_in, nodata_to_value=np.nan)
        self.send_info(nd_in)

        if self.method == "STANDARDISE":
            self.send_info("...standardising...")
            stdv = nd_in.std()
            mean = nd_in.mean()
            vals = '{0} std={1} mean={2}'.format(self.method, stdv, mean)
            nd_out = (nd_in - mean) / stdv

        elif self.method == "STRETCH":
            self.send_info("...standardising...")
            maxv = nd_in.max()
            minv = nd_in.min()
            vals = '{0} old_max={1} old_min={2} new_max={3} new_min={4}'.format(self.method, maxv, minv, self.max_stretch, self.min_stretch)
            nd_out = (nd_in - minv) * self.max_stretch / (maxv - minv) + self.min_stretch

        elif self.method == "NORMALISE":
            self.send_info("...normalising...")
            maxv = nd_in.max()
            minv = nd_in.min()
            vals = '{0} old_max={1} old_min={2} new_max={3} new_min={4}'.format(self.method, maxv, minv, self.max_stretch, self.min_stretch)
            nd_out = (nd_in - minv) / (maxv - minv)

        elif self.method == "LOG":
            self.send_info("...logarithmicising...")
            vals = '{0}'.format(self.method)
            nd_out = nd_in.log()

        elif self.method == "SQUAREROOT":
            self.send_info("...square-rooting...")
            vals = '{0}'.format(self.method)
            nd_out = r_in.sqrt()

        elif self.method == "INVERT":
            self.send_info("...inverting...")
            maxv = nd_in.max()
            minv = nd_in.min()
            vals = '{0} max={1} min={2}'.format(self.method, maxv, minv)
            nd_out = (nd_in - (maxv + minv)) * -1

        # save and exit
        arcpy.env.overwriteOutput = True
        arcpy.env.outputCoordinateSystem = r_in
        arcpy.env.cellSize = r_in
        ras_out = arcpy.NumPyArrayToRaster(nd_out, value_to_nodata=np.nan)
        ras_out.save(r_out)
        self.results.add({"geodata": r_out, "source_geodata": r_in, "transform": vals})
        return
