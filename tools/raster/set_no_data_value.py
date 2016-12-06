from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, raster_formats
from arcpy.sa import Con, IsNull

tool_settings = {"label": "Set NoData Value",
                 "description": "Set NoData Value...",
                 "can_run_background": "True",
                 "category": "Raster"}

@results
@geodata
class SetNodataValueRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.ndv = None
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("ndv", "NoData Value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.ndv = float(p["ndv"])
        self.raster_format = "" if p['raster_format'].lower == 'esri grid' else p["raster_format"]  # fix output extension

    def iterate(self):
        self.iterate_function_on_tableview(self.set_ndv, "raster_table", ["raster"])
        return

    def set_ndv(self, data):
        ras = data['raster']
        self.geodata.validate_geodata(ras, raster=True)

        r_out = self.geodata.make_raster_name(ras, self.results.output_workspace, self.raster_format)

        self.send_info("Setting NDV {0} into {1} -> {2}".format(self.ndv, ras, r_out))
        null_ras = IsNull(ras)
        self.send_info("done isnull")
        out_ras = Con(null_ras, self.ndv, ras, "#")
        self.send_info("done con")
        out_ras.save(r_out)

        self.results.add({"geodata": r_out, "source_geodata": ras})
        return
