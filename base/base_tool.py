# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 10:48:26 2016

@author: byed
"""
import utils
import os
import contextlib
import ast
from base.class_decorators import arcmap
from base.geodata import get_search_cursor_rows, is_file_system


@arcmap
class BaseTool(object):
    def __init__(self, settings):
        """Define the tool (tool name is the name of the class)."""
        # the essentials
        self.label = settings.get("label", "label not set")
        self.description = settings.get("description", "description not set")
        self.canRunInBackground = settings.get("can_run_background", False)
        self.category = settings.get("category", False)
        self.stylesheet = self.set_stylesheet()
        # hold refs to arcgis args passed to Execute()
        self.arc_parameters = []
        self.arc_messages = None
        # used as stamp for default names etc.
        self.tool_type = type(self).__name__
        self.tool_time_open = utils.time_stamp()
        self.run_id = "{0}_{1}".format(self.tool_type, self.tool_time_open)
        # instance specific
        self.execution_list = []
        self.metadata = {}
        # state
        self.current_geodata = self.current_row = "Not set"

    @staticmethod
    def set_stylesheet():
        style_path = os.path.split(os.path.realpath(__file__))[0]  # base
        style_path = os.path.split(style_path)[0]  # grid_garage_3
        style_path = os.path.join(style_path, "style")
        xls1 = os.path.join(style_path, "MdDlgContent.xsl")
        xls2 = os.path.join(style_path, "MdDlgHelp.xsl")
        return ";".join([xls1, xls2])

    @contextlib.contextmanager
    def error_handler(self):
        try:
            yield
        except Exception as e:
            self.send_warning(e)
            if hasattr(self, "results"):
                self.results.fail(self.current_geodata, e, self.current_row)

    @staticmethod
    def evaluate(node_or_string):
        return ast.literal_eval(node_or_string)

    def get_parameter_by_name(self, param_name):
        if not self.arc_parameters:
            return

        for param in self.arc_parameters:
            n = getattr(param, "name", None)
            if n == param_name:
                return param

        raise ValueError("Parameter {0} not found".format(param_name))

    def getParameterInfo(self):
        """Define parameter definitions"""
        return []

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        out_tbl_par = None
        for p in parameters:
            if p.name == "result_table_name":
                out_tbl_par = p
                break

        # default table name
        if out_tbl_par.value == "#run_id#":
            out_tbl_par.value = self.run_id

    def updateMessages(self, parameters):
        out_ws_par = None
        out_rasfmt_par = None
        for p in parameters:
            if p.name == "output_workspace":
                out_ws_par = p
                continue
            elif p.name == "raster_format":
                out_rasfmt_par = p
                continue

        if out_ws_par and out_rasfmt_par:
            out_ws_par.clearMessage()
            out_rasfmt_par.clearMessage()
            if out_ws_par.altered or out_rasfmt_par.altered:
                ws = out_ws_par.value
                if is_file_system(ws) and out_rasfmt_par.value == "Esri Grid":
                    out_rasfmt_par.setErrorMessage("Invalid raster format for workspace type")

        # BaseTool.updateMessages(self, parameters)
        # stretch = parameters[2].value == 'STRETCH'
        # if stretch and not parameters[3].valueAsText:
        #     parameters[3].setIDMessage("ERROR", 735, parameters[3].displayName)
        # if stretch and not parameters[4].valueAsText:
        #     parameters[4].setIDMessage("ERROR", 735, parameters[4].displayName)
        return

        # for p in parameters:
        #     v = p.value
        #     if v == "#run_id#":
        #         p.value = self.run_id
        #         break
        # # raster format in workspace
        # for p in parameters:
        #     if p.name == "raster_format":


        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # self.send_info("BaseTool.execute()")

        # check if we have a function to run
        if not self.execution_list:
            raise ValueError("Tool execution list is empty")

        # set the runtime object refs
        self.arc_parameters = parameters
        self.arc_messages = messages

        if hasattr(self, "results"):
            self.send_info(self.results.initialise(self.get_parameter_dict(["result_table", "fail_table"])))

        # run the functions
        for f in self.execution_list:
            if isinstance(f, (list, tuple)):  # expecting to feed a function a function
                f1, f2 = f  # for now just limit to 2 deep
                f1(f2)
            else:  # normal case, expecting a function
                f()

        if hasattr(self, "results"):
            self.send_info(self.results.write())

        return

    def get_parameter_dict(self, leave_as_object=()):
        return {p.name: p if p.name in leave_as_object else p.valueAsText for p in self.arc_parameters}

    def get_parameter_names(self):
        return [p.name for p in self.arc_parameters]

    def iterate_function_on_tableview(self, func, parameter_name, key_names):

        param = self.get_parameter_by_name(parameter_name)
        if param.datatype != "Table View":
            raise ValueError("That parameter is not a table or table view ({0})".format(param.name))

        multi_val = getattr(param, "multivalue", False)
        if multi_val:
            raise ValueError("Multi value tableview iteration is not yet implemented")

        v = param.valueAsText

        # map fields
        num_fields = len(key_names)                                                          # [rf1, rf2, ...]
        f_names = ["{0}_field_{1}".format(parameter_name, i) for i in range(0, num_fields)]  # [f_0, f_1, ...]
        f_vals = [self.get_parameter_by_name(f_name).valueAsText for f_name in f_names]

        rows = get_search_cursor_rows(v, f_vals)

        # iterate
        total_items, count = len(rows), 0
        self.send_info("{0} items to process".format(total_items))
        for r in rows:
            with self.error_handler():
                count += 1
                r = utils.make_tuple(r)
                self.current_row = r
                data = {k: v for k, v in zip(key_names, r)}
                g = data.get(key_names[0], None)  # convention: first key is geodata
                self.current_geodata = g
                func(data)

        return

    def iterate_function_on_parameter(self, func, parameter_name, key_names):
        param = self.get_parameter_by_name(parameter_name)
        multi_val = getattr(param, "multivalue", False)

        if param.datatype == "Table View":
            raise ValueError("Function deprecation, use 'iterate_function_on_tableview'")

        rows = param.valueAsText.split(";") if multi_val else [param.valueAsText]

        if not rows:
            raise ValueError("No values to process.")

        # iterate
        total_items, count = len(rows), 0
        self.send_info("{0} items to process".format(total_items))
        for r in rows:
            with self.error_handler():
                self.send_info(r)
                count += 1
                r = utils.make_tuple(r)
                self.current_row = r
                data = {k: v for k, v in zip(key_names, r)}
                g = data.get("geodata", None)
                self.current_geodata = g

                func(data)

        return

    def send_info(self, message):
        if not self.arc_messages:
            print message
        else:
            self.arc_messages.addMessage(message)

    def send_warning(self, message):
        if not self.arc_messages:
            print message
        else:
            self.arc_messages.addWarningMessage(message)
