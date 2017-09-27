from base.base_tool import BaseTool
from base import utils
from base.decorators import input_tableview, input_output_table, parameter
from collections import OrderedDict


tool_settings = {"label": "Export tips",
                 "description": "Exports tips...",
                 "can_run_background": "False",
                 "category": "Metadata"}


class ExportTipsToFileMetadataTool(BaseTool):
    """
    """
    def __init__(self):
        """

        """

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

    @input_tableview()
    @parameter("include_fields", "Include Fields", "Field", "Required", True, "Input", None, None, ["tip_table"], None, None)
    @parameter("tip_folder", "Folder for Tip Files", "DEFolder", "Required", False, "Input", None, None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.export, "tip_table", ["geodata"], nonkey_names=self.include_fields.split(";") , return_to_results=True)

        return

    def export(self, data):
        """

        Args:
            data:

        Returns:

        """

        geodata = data["geodata"]

        utils.validate_geodata(geodata)

        self.info("Creating TIP file for {0}".format(geodata))

        tip_order = data["tip_order"].split(",")

        ordered_fields = [f for f in tip_order if f in self.include_fields]

        tip_dic = OrderedDict()
        for tip_field in ordered_fields:
            tip_dic[tip_field] = data[tip_field]

        fpath, fname, fbase, fext = utils.split_up_filename(geodata)

        tip_file = utils.join_up_filename(self.tip_folder, fbase, ".tip")

        with open(tip_file, "w") as tipfile:
            for k, v in tip_dic.iteritems():
                tipfile.write("{0}: {1}\n".format(k, v))

        return {"geodata": geodata, "tip_file": tip_file}

