from base.base_tool import BaseTool
import base.arcmap
from base.decorators import input_tableview


tool_settings = {"label": "Display",
                 "description": "Adds geodata to ArcMap document",
                 "can_run_background": False,
                 "category": "Geodata"}


class DisplayGeodataTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview()
    def getParameterInfo(self):
        """Define parameter definitions"""
        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.display_geodata, "geodata_table", ["geodata"])

        return

    def display_geodata(self, data):
        """

        Args:
            data:
        """

        geodata = data["geodata"]

        try:  # see if it's a layer

            base.arcmap.add_layer(geodata, "BOTTOM")
            self.info("Added layer {0} to display".format(geodata))

        except Exception:
            try:  # see if it's a table

                base.arcmap.add_tableview(geodata)
                self.info("Added table {0} to display".format(geodata))

            except Exception as e:  # bugger it for now

                self.warn("Could not add {0} to display: {1}".format(geodata, str(e)))

        finally:
            # Refresh things
            base.arcmap.refresh_active_view()
            base.arcmap.refresh_toc()

