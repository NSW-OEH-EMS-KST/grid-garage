from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview

tool_settings = {"label": "Rename",
                 "description": "Renames datasets to a new name specified in the 'new name' field...",
                 "can_run_background": "True",
                 "category": "Geodata"}


@geodata
@results
class RenameGeodataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.start_iteration]

    @input_tableview("geodata_table", "Table for Geodata", False, ["new name:candidate_name:", "geodata:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def start_iteration(self):
        self.iterate_function_on_tableview(self.process, "geodata_table", ["geodata", "new name"])
        return

    def process(self, data):
        gd = data["geodata"]
        ngd = data["new name"]

        self.send_info('Renaming {0} --> {1}'.format(gd, ngd))
        self.geodata.rename(gd, ngd)

        self.results.add({'geodata': ngd, 'previous_name': gd})
        return

