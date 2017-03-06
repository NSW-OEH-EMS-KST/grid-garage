from base.base_tool import BaseTool
from base.geodata import raster_formats, resample_methods
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter
from arcpy import ProjectRaster_management, SpatialReference

tool_settings = {"label": "Reproject",
                 "description": "Reproject rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}

@geodata
@results
class ReprojectRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.out_fmt = self.out_cs = self.cellsz = self.resamp = self.rego = self.overrides = None
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
        self.log.debug("IN")

        pd = self.get_parameter_dict()
        self.log.debug(pd)
        self.out_fmt = "" if pd['raster_format'].lower == 'esri grid' else pd["raster_format"]  # fix output extension
        self.out_cs = self.arc_parameters[2].value
        self.cellsz = "#" if not pd["cell_size"] else str(pd['cell_size'])  # this seemed to solve an issue with unicode... strange
        self.resamp = "#" if not pd["resample_type"] else pd['resample_type']
        self.rego = "#" if not pd['rego_point'] else pd['rego_point']  # fix empty value for arcgis
        if pd["overrides"]:
            self.overrides = pd["overrides"].replace(" ", "").split(",")  # now a list "a:b, c:d, ..."
            self.overrides = {k: v for k, v in (override.split(":") for override in self.overrides)}   #if self.overrides else {"none": None}  # now a dict {a:b, c:d, ...}
        self.log.info("Transformation overrides: {0}".format(self.overrides))
        self.log.info("Output CS: {0}".format(self.out_cs.name))

        self.log.debug("OUT")
        return

    def iterate(self):
        self.iterate_function_on_tableview(self.reproject, "raster_table", ["raster"])
        return

    def reproject(self, data):
        self.log.debug("IN")

        r_in = data['raster']
        self.geodata.validate_geodata(r_in, raster=True, srs_known=True)
        # self.log.debug("1")

        r_out = self.geodata.make_raster_name(r_in, self.results.output_workspace, self.out_fmt)
        # self.log.debug("2")
        tx = self.geodata.get_transformation(r_in, self.out_cs, self.overrides)

        # do the business
        self.log.info("Projecting {0} into {1} -> {2}".format(r_in, self.out_cs.name, r_out))
        ProjectRaster_management(r_in, r_out, self.out_cs, geographic_transform=tx, resampling_type=self.resamp, cell_size=self.cellsz, Registration_Point=self.rego)

        r = self.results.add({"geodata": r_out, "source": r_in, "metadata": "to do"})
        self.log.info(r)

        self.log.debug("OUT")
        return

    # def execute(self, parameters, messages):
    #     # just to get this fucking parameter as an object!
    #     self.out_cs = parameters[2].value
    #     self.send_info("SRS= " + str(self.out_cs))
    #     self.send_info("srs type= " + str(type(self.out_cs)))
    #     BaseTool.execute(self, parameters, messages)
