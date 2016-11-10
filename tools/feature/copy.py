from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview
from os.path import splitext

tool_settings = {"label": "Copy",
                 "description": "Copies...",
                 "can_run_background": "True",
                 "category": "Feature"}


@geodata
@results
class CopyFeatureTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("features_table", "Table for Features", False, ["feature:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterate(self):
        self.iterate_function_on_tableview(self.process, "features_table", ["feature"])
        return

    def process(self, data):
        fc = data["feature"]
        self.geodata.validate_geodata(fc, vector=True)

        ws = self.results.output_workspace
        ex = splitext(fc)[1]
        nfc = self.geodata.make_featureclass_name(fc, ws, ex)

        self.send_info('copying {0} --> {1}'.format(fc, nfc))
        self.geodata.copy_feature(fc, nfc)

        self.results.add({'geodata': nfc, 'copied_from': fc})
        return

