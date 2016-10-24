from base.base_tool import BaseTool
from base.class_decorators import geodata, results
from base.method_decorators import input_output_table, input_tableview, parameter
from base.utils import split_up_filename, join_up_filename

tool_settings = {"label": "Generate Names",
                 "description": "Generates candidate dataset names for later use in the 'Rename' Tool...",
                 "can_run_background": "True",
                 "category": "Geodata"}


@geodata
@results
class GenerateNamesGeodataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterating]
        self.prefix = self.suffix = self.replacements = None

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @parameter("replacements", "Replacements", "GPString", "Optional", False, "Input", None, None, None, None)
    @parameter("prefix", "Prefix", "GPString", "Optional", False, "Input", None, None, None, None)
    @parameter("suffix", "Suffix", "GPString", "Optional", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def test_duplicates(self):
        pass
        # """
        # Test for duplicate names.
        #
        # """
        # tool.info('Testing new names for duplication...')
        # table = tool.get_parameter_as_text(0)
        # rows = tool.search_cursor(table, ['candidate_item'])
        # value_set = set()
        # i = 0
        # for x, in rows:
        #     value_set.add(x)
        #     i += 1
        # value_set = sorted(value_set)
        # if len(value_set) == i:
        #     tool.info('New item names (full) appear to be unique. Das is gut.')
        # else:
        #     tool.warn('!* There may be non-unique new names. doh! Please check.')

    def initialise(self):
        pars = self.get_parameter_dict()
        self.prefix = pars.get("prefix", None)
        self.suffix = pars.get("suffix", None)
        self.replacements = pars.get("replacements", None)

        # look for an early exit as all parameters are optional
        if not (self.replacements or self.prefix or self.suffix):
            self.send_warning('All optional parameters are empty. Nothing to do.')
            exit(1)

        if self.replacements:  # s_,; p_,prefix_
            try:
                replace = self.replacements
                replace = replace.split(';')  # ["s_,", "p_,prefix_"]
                replace = [v.replace("'", "").replace('"', "").replace(" ", "") for v in replace]
                replace = [v.split(",") for v in replace]  # [["s_", ""], ["p_", "prefix"]]
                # get rid of blanks and quotes - don't want them in geodata names
                replace = [[v1.replace("'", "").replace(" ", "_"), v2.replace("'", "").replace(" ", "_")] for v1, v2 in replace]
                self.replacements = replace
            except:
                raise ValueError('Could not parse replacements string! It should be like "old", "new"; "next_old", "next_new"')

            # reflect the changes
            self.send_info('Replacements to be made are: {0}'.format(replace))

    def iterating(self):
        self.iterate_function_on_tableview(self.process, "geodata_table", ["geodata"])
        return

    def process(self, data):
        """ Make a candidate name from the original"""
        gd = data["geodata"]

        # get the current name elements
        ws, old_base, old_name, old_ext = split_up_filename(gd)

        # start with the current name
        new_name = old_name

        if self.replacements:
            for chars, new_chars in self.replacements:
                new_name = new_name.replace(chars, new_chars)

        new_name = self.prefix + new_name if self.prefix else new_name
        new_name = new_name + self.suffix if self.suffix else new_name
        new_name = new_name + old_ext if old_ext else new_name

        new_full = join_up_filename(ws, new_name)

        self.send_info("{0} -->> {1}".format(old_base, new_name))

        # done
        self.results.add({'geodata': gd, 'candidate_geodata': new_full, 'existing_base_name': old_base, 'candidate_base_name': new_name})
        return
