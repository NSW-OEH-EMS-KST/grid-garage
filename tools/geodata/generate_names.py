import base.base_tool
import base.results
from base.method_decorators import input_output_table_with_output_affixes, input_tableview, parameter
from base.utils import split_up_filename, is_raster, is_vector, make_raster_name, make_vector_name, make_table_name


tool_settings = {"label": "Generate Names",
                 "description": "Generates candidate dataset names for later use in the 'Rename' Tool...",
                 "can_run_background": "True",
                 "category": "Geodata"}


@base.results.result
class GenerateNamesGeodataTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]

        return

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @parameter("replacements", "Replacements", "GPString", "Optional", False, "Input", None, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

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

        # look for an early exit as all parameters are optional
        if not (self.replacements or self.output_filename_prefix or self.output_filename_suffix):
            self.send_warning('All optional parameters are empty. Nothing to do.')
            exit(1)

        if self.replacements:                                                                        # s_,; p_,prefix_
            try:
                replace = self.replacements
                replace = replace.split(';')                                                         # ["s_,", "p_,prefix_"]
                replace = [v.replace("'", "").replace('"', "").replace(" ", "") for v in replace]
                replace = [v.split(",") for v in replace]                                            # [["s_", ""], ["p_", "prefix"]]
                # get rid of blanks and quotes - don't want them in geodata names
                replace = [[v1.replace("'", "").replace(" ", "_"), v2.replace("'", "").replace(" ", "_")] for v1, v2 in replace]
                self.replacements = replace
            except:
                raise ValueError('Could not parse replacements string! It should be like "old", "new"; "next_old", "next_new"')

            # reflect the changes
            self.log.info('Replacements to be made are: {0}'.format(replace))

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.process, "geodata_table", ["geodata"])

        return

    def process(self, data):

        """ Make a candidate name from the original"""
        gd = data["geodata"]

        # get the current name elements
        old_ws, old_base, old_name, old_ext = split_up_filename(gd)

        # start with the current name
        new_name = old_name

        if self.replacements:
            for chars, new_chars in self.replacements:
                new_name = new_name.replace(chars, new_chars)

        # get the new name elements for validation
        new_ws, new_base, new_name, new_ext = split_up_filename(new_name)
        if is_raster(gd):
            new_full = make_raster_name(new_name, old_ws, old_ext, self.output_filename_prefix, self.output_filename_suffix)
        elif is_vector(gd):
            new_full = make_vector_name(new_name, old_ws, old_ext, self.output_filename_prefix, self.output_filename_suffix)
        else:
            new_full = make_table_name(new_name, old_ws, old_ext, self.output_filename_prefix, self.output_filename_suffix)

        self.log.info("{0} -->> {1}".format(gd, new_full))
        self.results.add({'geodata': gd, 'candidate_name': new_full, 'existing_base_name': old_base, 'candidate_base_name': new_base})

        return
