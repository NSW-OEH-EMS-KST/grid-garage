from base.base_tool import BaseTool
from base.results import result
from base.utils import raster_formats, resample_methods, validate_geodata, make_raster_name, get_transformation
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter
import arcpy

tool_settings = {"label": "Reproject",
                 "description": "Reproject rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class ReprojectRasterTool(BaseTool):

    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("output_cs", "Output Spatial Reference", "Spatial Reference", "Required", False, "Input", None, "outputCoordinateSystem", None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("resample_type", "Resampling Method", "GPString", "Required", False, "Input", resample_methods, "resamplingMethod", None, None)
    @parameter("rego_point", "Registration Point", "GPPoint", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("overrides", "Transformation Overrides", "GPString", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def initialise(self):

        self.debug("initialise locals={}".format(locals()))

        self.output_cs = self.parameters[2].value  # need the object for later code to work
        self.cell_size = str(self.cell_size)  # this seemed to solve an issue with unicode... strange

        if self.overrides != "#":
            try:
                self.overrides = self.overrides.replace(" ", "").split(",")  # now a list "a:b, c:d, ..."
                self.overrides = {k: v for k, v in (override.split(",") for override in self.overrides)}   #if self.overrides else {"none": None}  # now a dict {a:b, c:d, ...}
            except:
                raise ValueError("There is a problem with specified overrides. should be something like 'a:b, c:d,...'")

        self.info(["Transformation overrides: {0}".format(self.overrides), "Output CS: {0}".format(self.output_cs.name)])

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.reproject, "raster_table", ["geodata"], return_to_results=True)

        return

    def reproject(self, data):

        r_in = data['geodata']

        validate_geodata(r_in, raster=True, srs_known=True)

        r_out = make_raster_name(r_in, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        tx = get_transformation(r_in, self.output_cs, self.overrides)

        self.info("Projecting {0} into {1} -> {2}".format(r_in, self.output_cs.name, r_out))

        arcpy.ProjectRaster_management(r_in, r_out, self.output_cs, geographic_transform=tx, resampling_type=self.resample_type, cell_size=self.cell_size, Registration_Point=self.rego_point)

        return {"geodata": r_out, "source": r_in}
