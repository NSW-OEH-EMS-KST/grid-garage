import base.base_tool

from base.decorators import input_output_table, input_tableview
from arcpy import Rename_management

tool_settings = {"label": "Rename",
                 "description": "Renames datasets to a new name specified in the 'new name' field...",
                 "can_run_background": "True",
                 "category": "Geodata"}


class RenameGeodataTool(base.base_tool.BaseTool):

    def __init__(self):
        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("geodata_table", "Table of Geodata", other_fields=["candidate_name", "New Name", "Required", "candidate_name"])
    @input_output_table
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.rename, "geodata_table", ["geodata", "candidate_name"], return_to_results=True)

        return

    def rename(self, data):

        gd = data["geodata"]
        ngd = data["candidate_name"]

        self.info('Renaming {0} --> {1}'.format(gd, ngd))
        Rename_management(gd, ngd)

        return {'geodata': ngd, 'previous_name': gd}

