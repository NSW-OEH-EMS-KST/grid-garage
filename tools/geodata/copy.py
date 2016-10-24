from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview

tool_settings = {"label": "Copy",
                 "description": "Copies...",
                 "can_run_background": "True",
                 "category": "Geodata"}


@geodata
@results
class CopyGeodataTool(BaseTool):
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
        self.send_info(data)

        gd = data["geodata"]
        ws = self.output_workspace

        ngd = self.geodata.make_name(gd, ws)
        self.send_info('copying {0} --> {1}'.format(gd, ngd))

        self.geodata.copy(gd, ngd)

        self.results.add({'geodata': ngd, 'copied_from': gd})
        return

