from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview

tool_settings = {"label": "Copy",
                 "description": "Copies...",
                 "can_run_background": "True",
                 "category": "Feature"}


@geodata
@results
class CopyFeatureTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterating]

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterating(self):
        self.iterate_function_on_tableview(self.process, "geodata_table", ["geodata"])
        return

    def process(self, data):
        fc = data["geodata"]
        self.geodata.validate_geodata(fc, vector=True)

        ws = self.results.output_workspace
        nfc = self.geodata.make_table_name(fc, ws)

        self.send_info('copying {0} --> {1}'.format(fc, nfc))
        self.geodata.copy_feature(fc, nfc)

        self.results.add({'geodata': nfc, 'copied_from': fc})
        return

