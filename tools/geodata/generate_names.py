import base.base_tool

from base.decorators import input_output_table, input_tableview, parameter
from base.utils import split_up_filename, is_raster, is_vector, make_table_name, make_table_name, make_table_name, get_search_cursor_rows


tool_settings = {"label": "Generate Names",
                 "description": "Generates candidate dataset names for later use in the 'Rename' Tool...",
                 "can_run_background": "True",
                 "category": "Geodata"}


class GenerateNamesGeodataTool(base.base_tool.BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate, self.test_duplicates]

        return

    @input_tableview()
    @parameter("replacements", "Replacements", "GPString", "Optional", False, "Input", None, None, None, None)
    @input_output_table(affixing=True, out_file_workspace=False)
    def getParameterInfo(self):
        """

        Returns:

        """

        return base.base_tool.BaseTool.getParameterInfo(self)

    def test_duplicates(self):
        """
        Test for duplicate names.

        """
        self.info('Testing new names for duplication...')
        table = self.result.pass_csv  # self.get_parameter_by_name("result_table").valueAsText()  # tool.get_parameter_as_text(0)
        self.debug(table)
        rows = get_search_cursor_rows(table, ['candidate_name'])
        self.debug(rows)
        values = [x for x, in rows]
        duplicates = set([x for x in values if values.count(x) > 1])
        duplicates = list(duplicates)  # nicer print

        if not duplicates:
            self.info('New item names (full) appear to be unique. Das is gut mein freund...')
        else:
            self.warn(['!! There seems to be non-unique new names. DOH! Please check the following...'] + duplicates)

    def initialise(self):
        """

        Returns:

        """

        # look for an early exit as all parameters are optional
        if not (self.output_filename_prefix or self.output_filename_suffix) and self.replacements == "#":
            self.warn('All optional parameters are empty. Nothing to do.')
            exit(1)

        if self.replacements == "#":

            self.info('No text replacements to be made')
            self.replacements = None
        else:

            try:
                replace = self.replacements                                                          # s_,; p_,prefix_
                replace = replace.split(';')                                                         # ["s_,", "p_,prefix_"]
                replace = [v.replace("'", "").replace('"', "").replace(" ", "") for v in replace]
                replace = [v.split(",") for v in replace]                                            # [["s_", ""], ["p_", "prefix"]]
                # get rid of blanks and quotes - don't want them in geodata names
                replace = [[v1.replace("'", "").replace(" ", "_"), v2.replace("'", "").replace(" ", "_")] for v1, v2 in replace]
                self.replacements = replace
                self.info('Replacements to be made are: {0}'.format(self.replacements))
            except:
                raise ValueError('Could not parse replacements string! It should be like "old", "new"; "next_old", "next_new"')

        return

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.process, return_to_results=True)

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
            new_full = make_table_name(new_name, old_ws, old_ext, self.output_filename_prefix, self.output_filename_suffix)
        elif is_vector(gd):
            new_full = make_table_name(new_name, old_ws, old_ext, self.output_filename_prefix, self.output_filename_suffix)
        else:
            new_full = make_table_name(new_name, old_ws, old_ext, self.output_filename_prefix, self.output_filename_suffix)

        self.info("{0} -->> {1}".format(gd, new_full))

        return {'geodata': gd, 'candidate_name': new_full, 'existing_base_name': old_base, 'candidate_base_name': new_base}
