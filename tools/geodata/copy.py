import base.base_tool
import base.results
from base.method_decorators import input_output_table_with_output_affixes, input_tableview
from os.path import splitext
from base.utils import make_table_name
from arcpy import Copy_management

tool_settings = {"label": "Copy",
                 "description": "Make a simple copy of geodata",
                 "can_run_background": "True",
                 "category": "Geodata"}


@base.results.result
class CopyGeodataTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.copy, "geodata_table", ["geodata"])

        return

    def copy(self, data):
        gd = data["geodata"]

        ws = self.results.output_workspace
        ex = splitext(gd)[1]
        ngd = make_table_name(gd, ws, ex, self.output_filename_prefix, self.output_filename_suffix)

        self.log.info('Copying {0} --> {1}'.format(gd, ngd))
        Copy_management(gd, ngd)

        r = self.results.add({'geodata': ngd, 'copied_from': gd})
        self.log.info(r)

        return

# Copy_management(in_data, out_data, {data_type})
# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy.htm"
