from base.base_tool import BaseTool

from base.decorators import input_output_table, parameter

tool_settings = {"label": "Select",
                 "description": "Feed selected geodata into a table",
                 "can_run_background": "True",
                 "category": "Geodata"}


class SelectGeodataTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @parameter("geodata", "Select Geodata", "GPType", "Required", True, "Input", None, None, None, None)
    @input_output_table()
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_parameter(self.process)

        return

    def process(self, data):
        """

        Args:
            data:

        Returns:

        """

        self.result.add_pass(data)

        return

