from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter, raster_formats
from arcpy.sa import SetNull

tool_settings = {"label": "Set Value to Null",
                 "description": "Sets...",
                 "can_run_background": "True",
                 "category": "Raster"}

@results
@geodata
class SetValueToNullRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.val_to_null = None
        self.raster_format = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("val_to_null", "Value to Set Null", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, "Esri Grid")
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.val_to_null = p["val_to_null"]
        self.raster_format = "" if p['raster_format'].lower == 'esri grid' else p["raster_format"]

    def iterate(self):
        self.iterate_function_on_tableview(self.set_null, "raster_table", ["raster"])
        return

    def set_null(self, data):
        r_in = data['raster']
        self.geodata.validate_geodata(r_in, raster=True)

        r_out = self.geodata.make_raster_name(r_in, self.results.output_workspace, self.raster_format)

        self.send_info("Setting values of {0} to Null in {1} -> {2}".format(self.val_to_null, r_in, r_out))

        out_ras = SetNull(r_in, r_in, 'VALUE = {0}'.format(self.val_to_null))
        out_ras.save(r_out)

        self.results.add({"geodata": r_out, "source_geodata": r_in})
        return


