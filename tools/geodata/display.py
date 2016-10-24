from base.base_tool import BaseTool
from base.method_decorators import input_tableview

tool_settings = {"label": "Display",
                 "description": "Adds geodata to ArcMap document",
                 "can_run_background": False,
                 "category": "Geodata"}


class DisplayGeodataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.start_iteration]

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    def getParameterInfo(self):
        """Define parameter definitions"""
        return BaseTool.getParameterInfo(self)

    def start_iteration(self):
        """The source code of the tool"""
        with self.error_handler():
            self.iterate_function_on_tableview(self.display_geodata, "geodata_table", ["geodata"])

    def display_geodata(self, data):
        geodata = data["geodata"]
        try:
            # see if it's a layer
            self.arcmap.add_layer(geodata, "BOTTOM")
            self.send_info("Added layer {0} to display".format(geodata))
        except Exception:
            try:
                # see if it's a table
                self.arcmap.add_tableview(geodata)
                self.send_info("Added table {0} to display".format(geodata))
            except Exception as e:
                # bugger it for now
                self.send_warning("Could not add {0} to display: {1}".format(geodata, str(e)))
        finally:
            # Refresh things
            self.arcmap.refresh_active_view()
            self.arcmap.refresh_toc()

