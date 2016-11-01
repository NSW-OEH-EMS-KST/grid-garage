from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter

tool_settings = {"label": "Tweak Values",
                 "description": "Tweaks...",
                 "can_run_background": "True",
                 "category": "Raster TODO"}


@results
@geodata
class TweakValuesRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.min_val = None
        self.under_min = None
        self.max_val = None
        self.over_max = None
        self.scaler = None
        self.constant = None
        self.integerise = None

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("min_val", "Minimum value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("under_min", "Values < Minumium", "GPString", "Required", False, "Input", ["Minimum", "NoData"], None, None, "Minimum")
    @parameter("max_val", "Maximum value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("over_max", "Values > Maxumium", "GPString", "Required", False, "Input", ["Maximum", "NoData"], None, None, "Maximum")
    @parameter("scaler", "Scale Factor", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("constant", "Constant Shift", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("integerise", "integerise", "GPBoolean", "Required", False, "Input", None, None, None, False)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.integerise = p["min_val"]
        self.integerise = p["under_min"]
        self.integerise = p["max_val"]
        self.integerise = p["over_max"]
        self.integerise = p["scaler"]
        self.integerise = p["constant"]
        self.integerise = p["integerise"]

    def iterate(self):
        self.iterate_function_on_tableview(self.tweak, "geodata_table", ["geodata"])
        return

    def tweak(self, data):
        self.send_info(data)
        # self.add_result("TODO")
        return

