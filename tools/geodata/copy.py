from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview
from os.path import splitext

tool_settings = {"label": "Copy",
                 "description": "Make a simple copy of geodata",
                 "can_run_background": "True",
                 "category": "Geodata"}


@geodata
@results
class CopyGeodataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def iterate(self):
        self.iterate_function_on_tableview(self.process, "geodata_table", ["geodata"])
        return

    def process(self, data):
        gd = data["geodata"]
        ws = self.results.output_workspace
        ex = splitext(gd)[1]
        ngd = self.geodata.make_table_name(gd, ws, ex)

        self.send_info('copying {0} --> {1}'.format(gd, ngd))
        # Copy_management(in_data, out_data, {data_type})
        self.geodata.copy_geodata(gd, ngd)

        self.results.add({'geodata': ngd, 'copied_from': gd})
        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy.htm"