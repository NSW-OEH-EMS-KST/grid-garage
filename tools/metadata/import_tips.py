from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table
from collections import OrderedDict
import os


tool_settings = {"label": "Import Tip Files to Table",
                 "description": "Create a table of tips from existing tip files",
                 "can_run_background": "False",
                 "category": "Metadata"}


@result
class ImportTipFilesToTableMetadataTool(BaseTool):
    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.import_tip, "geodata_table", ["geodata"], return_to_results=True)

        return

    def import_tip(self, data):

        geodata = data["geodata"]
        utils.validate_geodata(geodata)

        fpath, fname, fbase, fext = utils.split_up_filename(geodata)

        tip_file = utils.join_up_filename(fpath, fbase, ".tip")

        if not os.path.exists(tip_file):
            raise ValueError("Tip file '{}' does not exist".format(tip_file))

        self.info("Parsing {0}".format(tip_file))

        tips = OrderedDict()
        tips["header"] = ""

        with open(tip_file, "r") as tipfile:
            buf = "header"
            for line in tipfile:
                s = line.strip().encode("ascii").split(":", 1)
                if len(s) > 1:
                    s1, s2 = s
                    buf = s1
                else:
                    s1 = s[0]
                    s2 = None
                if not s2:
                    tips[buf] += s1
                else:
                    tips[s1] = s2

        tips["field_order"] = tips.keys()

        res = {"geodata": geodata, "tip_file": tip_file}
        res.update(tips)

        return res


