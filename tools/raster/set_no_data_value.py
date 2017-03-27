import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats
import arcpy
import base.utils


tool_settings = {"label": "Set NoData Value",
                 "description": "Set NoData Value...",
                 "can_run_background": "True",
                 "category": "Raster"}

@base.results.result
class SetNodataValueRasterTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("ndv", "NoData Value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def initialise(self):
        self.ndv = float(self.ndv) if "." in self.ndv else int(self.ndv)

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.set_ndv, "raster_table", ["raster"])

        return

    def set_ndv(self, data):
        ras = data['raster']
        base.utils.validate_geodata(ras, raster=True)

        r_out = base.utils.make_raster_name(ras, self.results.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.log.info("Setting NDV {0} on {1} -> {2}".format(self.ndv, ras, r_out))
        null_ras = arcpy.sa.IsNull(ras)
        out_ras = arcpy.sa.Con(null_ras, self.ndv, ras, "#")
        out_ras.save(r_out)

        self.result.add({"geodata": r_out, "source_geodata": ras})

        return
