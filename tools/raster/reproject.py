from base.base_tool import BaseTool
from base.geodata import raster_formats, resample_methods, UnknownSrsError
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter
from arcpy import ProjectRaster_management

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
        self.out_fmt = self.out_cs = self.cellsz = self.resamp = self.rego = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @parameter("output_cs", "Output Coordinate System", "GPCoordinateSystem", "Required", False, "Input", None, "outputCoordinateSystem", None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
    @parameter("resample_type", "Resampling Method", "GPString", "Required", False, "Input", resample_methods, "resamplingMethod", None, None)
    @parameter("rego_point", "Registration Point", "GPPoint", "Optional", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        pd = self.get_parameter_dict()

        self.out_fmt = "" if pd['raster_format'].lower == 'esri grid' else pd["raster_format"]  # fix output extension
        self.out_cs = pd["output_cs"]
        self.cellsz = "#" if not pd["cell_size"] else pd['cell_size']
        self.resamp = "#" if not pd["resample_type"] else pd['resample_type']
        self.rego = "#" if not pd['rego_point'] else pd['rego_point']  # fix empty value for arcgis

        return

    def iterate(self):
        self.iterate_function_on_tableview(self.reproject, "raster_table", ["raster"])
        return

    def reproject(self, data):
        ras = data['raster']
        self.geodata.validate_geodata(ras, raster=True)
        d = self.geodata.describe(ras)
        r_srs = d.get("dataset_spatialReference", "Unknown")

        if "unknown" in r_srs.lower():
            raise UnknownSrsError(ras)

        r_out = self.geodata.make_raster_name(ras, self.results.output_workspace, self.out_fmt)

        tx = self.geodata.get_transformation(ras, self.out_cs)

        # self.send_info(str([self.out_cs, tx, self.cellsz, self.resamp, self.rego]))

        # do the business
        self.send_info("Projecting {0} into {1} -> {2}".format(ras, r_srs, r_out))
        ProjectRaster_management(ras, r_out, self.out_cs, geographic_transform=tx, resampling_type=self.resamp, cell_size=self.cellsz, Registration_Point=self.rego)

        self.results.add({"geodata": r_out, "source": ras, "metadata": "to do"})
        return

