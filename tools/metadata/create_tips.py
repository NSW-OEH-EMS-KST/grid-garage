from base.base_tool import BaseTool
from base.results import result
from base.utils import validate_geodata, describe
from base.method_decorators import input_tableview, input_output_table, parameter
from collections import OrderedDict


tool_settings = {"label": "Create Tips Table",
                 "description": "Create a table of tips from a tip file template",
                 "can_run_background": "False",
                 "category": "Metadata"}


@result
class CreateTipsTableMetadataTool(BaseTool):
    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.base_tips = None
        self.tip_order = []
        self.extractions = None

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @parameter("tip_template", "Tip Template", "GPTableView", "Required", False, "Input", None, None, None, None, None)
    @parameter("include_fields", "Include Fields", "Field", "Required", True, "Input", None, None, ["tip_template"], None, None)
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def initialise(self):

        self.include_fields = self.include_fields.split(";")
        self.info("Tip fields to be included are: {}".format(self.include_fields))

        with open(self.tip_template, "r") as tipfile:
            self.base_tips = [line.rstrip() for line in tipfile]

        if not self.base_tips:
            raise ValueError("Tip template table '{}' is empty".format(self.tip_template))

        base_tips = [line for line in self.base_tips if line]
        k = [x.strip() for x in base_tips[0].split(",")]
        v = [x.strip() for x in base_tips[1].split(",")]
        base_tips = [(k1, v1) for k1, v1 in zip(k, v) if k1 in self.include_fields]
        self.base_tips = OrderedDict(base_tips)
        self.tip_order = ",".join(self.base_tips.iterkeys())

        self.info("Base tips will be: {}".format(self.base_tips))

        def startsnends(string, code):
            return string.startswith(code) and string.endswith(code)

        self.extractions = {k: v for k, v in self.base_tips.iteritems() if startsnends(v.strip().strip('"'), "$")}
        self.info("Field values extraction from describe will: {}".format(self.extractions))

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.create, "geodata_table", ["geodata"], return_to_results=True)

        return

    def create(self, data):

        geodata = data["geodata"]

        validate_geodata(geodata)

        self.info("Building tips for {0}".format(geodata))

        r = {"geodata": geodata, "tip_order": self.tip_order}

        new_tips = OrderedDict()

        for k, v in self.base_tips.iteritems():
            new_tips[k] = v

        r.update(new_tips)

        fld_tips = {}
        for k, v in self.extractions.iteritems():   # "$table_fields,2#.html$"
            v = v.strip().strip('"').strip("$")     # table_fields,2#.html
            v = v.split("#")                        # ['table_fields,2', .html]
            text = v[1] if len(v) > 1 else ""       # .html

            v = v[0].split(":")                     # [table_fields, 2]
            field = v[0]                            # table_fields
            try:
                idx = int(v[1])-1 if len(v) > 1 else None      # 2
            except Exception as e:
                self.warn("Bad format '{}', use list:index (1-based)".format(v))
                fld_tips[k] = "{}{}".format("", text)
                continue

            desc = describe(geodata)
            try:
                new_val = desc[field]
            except [KeyError, AttributeError] as e:
                self.warn(": '{}' not in {}".format(field, desc.keys()))
                fld_tips[k] = "{}{}".format("", text)
                continue

            if idx:
                try:
                    new_val = new_val.split(",")
                    new_val = new_val[idx].strip()
                except IndexError as e:
                    self.warn("{} out of range {}: {}".format(idx+1, range(1, len(new_val)+1), new_val))
                    fld_tips[k] = "{}{}".format("", text)
                    continue

            fld_tips[k] = "{}{}".format(new_val, text)

        self.info("Extracted field values: {}".format(fld_tips))

        r.update(fld_tips)

        return r
