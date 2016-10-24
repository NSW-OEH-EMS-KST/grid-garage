from base.base_tool import BaseTool
from base.geodata import raster_formats, resample_methods
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
        self.execution_list = [self.initialise, self.iterating]
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

        self.out_fmt = "" if pd['output_format'].lower == 'esri grid' else pd["output_format"]  # fix output extension
        self.out_cs = pd["output_cs"]
        self.cellsz = pd["cell_size"]
        self.resamp = pd["resample_type"]
        self.rego = "#" if not pd['rego_point'] else pd['rego_point']  # fix empty value for arcgis

        return

    def iterating(self):
        self.iterate_function_on_tableview(self.reproject, "raster_table", ["raster"])
        return

    def reproject(self, data):
        r_in = data['raster']
        self.send_info(data)
        d = self.geodata.describe(r_in)
        r_srs = d.get("dataset_spatialReference", "Unknown")

        if "unknown" in r_srs.lower():
            raise ValueError("Raster dataset '{0}' has unknown spatial reference system ({1})".format(r_in, r_srs))

        r_out = self.geodata.make_raster_name(r_in, self.results.output_workspace, self.out_fmt)

        tx = self.geodata.get_transformation(r_in, self.out_cs)

        self.send_info(str([self.out_cs, tx, self.cellsz, self.resamp, self.rego]))

        # do the business
        self.send_info("Projecting {0} into {1} -> {2}".format(r_in, r_srs, r_out))
        ProjectRaster_management(r_in, r_out, self.out_cs, geographic_transform=tx, resampling_type=self.resamp, cell_size=self.cellsz, Registration_Point=self.rego)

        self.results.add({"geodata": r_out, "source": r_in, "metadata": "to do"})
        return

