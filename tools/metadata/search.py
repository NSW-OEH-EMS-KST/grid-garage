from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_tableview, input_output_table

tool_settings = {"label": "Search",
                 "description": "Search for metadata",
                 "can_run_background": "True",
                 "category": "Metadata TODO"}


@geodata
@results
class SearchMetadataTool(BaseTool):
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
        self.log.info(data)
        # TODO
        return


