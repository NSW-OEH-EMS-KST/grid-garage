from base.base_tool import BaseTool
from base.decorators import input_output_table, input_tableview
from os.path import splitext
from base.utils import make_table_name
from arcpy import Copy_management


tool_settings = {"label": "Copy",
                 "description": "Make a simple copy of geodata",
                 "can_run_background": "True",
                 "category": "Geodata"}


class CopyGeodataTool(BaseTool):
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
    @input_output_table(affixing=True)
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.copy, return_to_results=True)

        return

    def copy(self, data):
        """

        Args:
            data:

        Returns:

        """

        gd = data["geodata"]

        ext = splitext(gd)[1]

        ws = self.output_file_workspace or self.output_workspace

        ngd = make_table_name(gd, ws, ext, self.output_filename_prefix, self.output_filename_suffix)

        self.info('Copying {0} --> {1}'.format(gd, ngd))
        Copy_management(gd, ngd)

        return {'geodata': ngd, 'copied_from': gd}

# Copy_management(in_data, out_data, {data_type})
# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy.htm"
