from base.base_tool import BaseTool
from base.utils import raster_formats, resample_methods, validate_geodata, make_raster_name, get_transformation
from base.class_decorators import results
from base.method_decorators import input_tableview, input_output_table, parameter
from arcpy import ProjectRaster_management

tool_settings = {"label": "Reproject",
                 "description": "Reproject rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
class ReprojectRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("output_cs", "Output Spatial Reference", "Spatial Reference", "Required", False, "Input", None, "outputCoordinateSystem", None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("resample_type", "Resampling Method", "GPString", "Required", False, "Input", resample_methods, "resamplingMethod", None, None)
    @parameter("rego_point", "Registration Point", "GPPoint", "Optional", False, "Input", None, None, None, None)
    @parameter("overrides", "Transformation Overrides", "GPString", "Optional", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        self.log.debug("IN self.parameter_strings= {}".format(self.parameter_strings))

        self.output_cs = self.parameter_objects[2].value  # need the object for later code to work
        self.cell_size = str(self.cell_size)  # this seemed to solve an issue with unicode... strange
        if self.overrides:
            self.overrides = self.overrides.replace(" ", "").split(",")  # now a list "a:b, c:d, ..."
            self.overrides = {k: v for k, v in (override.split(":") for override in self.overrides)}   #if self.overrides else {"none": None}  # now a dict {a:b, c:d, ...}
        self.log.info("Transformation overrides: {0}".format(self.overrides))
        self.log.info("Output CS: {0}".format(self.output_cs.name))

        self.log.debug("OUT")
        return

    def iterate(self):
        self.iterate_function_on_tableview(self.reproject, "raster_table", ["raster"])
        return

    def reproject(self, data):
        self.log.debug("IN")

        r_in = data['raster']
        validate_geodata(r_in, raster=True, srs_known=True)

        r_out = make_raster_name(r_in, self.results.output_workspace, self.raster_format)
        tx = get_transformation(r_in, self.output_cs, self.overrides)

        # do the business
        self.log.info("Projecting {0} into {1} -> {2}".format(r_in, self.output_cs.name, r_out))
        ProjectRaster_management(r_in, r_out, self.output_cs, geographic_transform=tx, resampling_type=self.resample_type, cell_size=self.cell_size, Registration_Point=self.rego_point)

        r = self.results.add({"geodata": r_out, "source": r_in, "metadata": "to do"})
        self.log.info(r)

        self.log.debug("OUT")
        return
