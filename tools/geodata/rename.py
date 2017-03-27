import base.base_tool
import base.results
from base.method_decorators import input_output_table, input_tableview
from arcpy import Rename_management

tool_settings = {"label": "Rename",
                 "description": "Renames datasets to a new name specified in the 'new name' field...",
                 "can_run_background": "True",
                 "category": "Geodata"}


@base.results.result
class RenameGeodataTool(base.base_tool.BaseTool):

    def __init__(self):
        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("geodata_table", "Table for Geodata", False, ["new name:candidate_name:", "geodata:geodata:"])
    @input_output_table
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.rename, "geodata_table", ["geodata", "new name"])

        return

    def rename(self, data):

        gd = data["new name"]
        ngd = data["geodata"]

        self.log.info('Renaming {0} --> {1}'.format(gd, ngd))
        Rename_management(gd, ngd)

        r = self.result.add({'geodata': ngd, 'previous_name': gd})
        self.log.info(r)

        return

