# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 10:48:26 2016

@author: byed
"""
import utils
import os
import ast
import base.log
import base.utils
import arcpy


class BaseTool(object):

    @base.log.log
    def __init__(self, settings):
        """ Define the tool (tool name is the name of the class).
        Args:
            settings (): A dictionary implemented in derived classes
        """
        self.log = base.log  # avoid requiring an import for each tool module
        self.tool_type = type(self).__name__

        # the essentials
        self.label = settings.get("label", "label not set")
        self.description = settings.get("description", "description not set")
        self.canRunInBackground = settings.get("can_run_background", False)
        self.category = settings.get("category", False)
        self.stylesheet = self.set_stylesheet()

        # hold refs to arcgis args passed to Execute()
        self.parameter_strings = None
        self.parameter_objects = None
        self.arc_messages = None

        # used as stamp for default names etc.
        self.tool_time_open = utils.time_stamp()
        self.run_id = "{0}_{1}".format(self.tool_type, self.tool_time_open)

        # instance specific, set in derived classes
        self.execution_list = []
        self.metadata = {}

        return

    @staticmethod
    def set_stylesheet():
        """ Set the tool stylesheet.

        Returns:

        """
        style_path = os.path.split(os.path.realpath(__file__))[0]  # base
        style_path = os.path.split(style_path)[0]  # grid_garage_3
        style_path = os.path.join(style_path, "style")
        xls1 = os.path.join(style_path, "MdDlgContent.xsl")
        xls2 = os.path.join(style_path, "MdDlgHelp.xsl")
        return ";".join([xls1, xls2])

    @staticmethod
    def evaluate(node_or_string):
        return ast.literal_eval(node_or_string)

    @base.log.log
    def get_parameter_by_name(self, param_name, raise_not_found_error=False):
        """ Returns a parameter based on its name

        Args:
            param_name (): The name of the parameter to return

        Returns:

        """
        if self.parameter_objects:

            for param in self.parameter_objects:
                n = getattr(param, "name", None)
                if n == param_name:

                    return param

        if raise_not_found_error:
            raise ValueError("Parameter {0} not found".format(param_name))

        return

    @base.log.log
    def getParameterInfo(self):
        """Define parameter definitions"""
        return []

    @base.log.log
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    @base.log.log
    def updateParameters(self, parameters):
        """ Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.

        Args:
            parameters (): The tool parameters

        Returns:

        """

        out_tbl_par = None
        for p in parameters:
            if p.name == "result_table_name":
                out_tbl_par = p
                break

        # default table name
        if out_tbl_par and out_tbl_par.value == "#run_id#":
            out_tbl_par.value = self.run_id

        return

    @base.log.log
    def updateMessages(self, parameters):
        """

        Args:
            parameters (): The tool parameters

        Returns:

        """
        # out_ws_par = None
        # for p in parameters:
        #     if p.name == "output_workspace":
        #         out_ws_par = p
        #         break
        #
        # ras_fmt_par = None
        # for p in parameters:
        #     if p.name == "raster_format":
        #         ras_fmt_par = p
        #         break
        #
        # if out_ws_par and ras_fmt_par:
        #
        #     out_ws_par.clearMessage()
        #     ras_fmt_par.clearMessage()
        #     # base.log.debug("messages cleared")
        #
        #     if out_ws_par.altered or ras_fmt_par.altered:
        #         # base.log.debug("out_ws_par.altered or out_rasfmt_par.altered")
        #
        #         ws = out_ws_par.value
        #         fmt = ras_fmt_par.value
        #         # base.log.debug("ws={} fmt={}".format(ws, fmt))
        #         if base.utils.is_local_gdb(ws) and fmt != "Esri Grid":
        #             ras_fmt_par.setErrorMessage("Invalid raster format for workspace type")
        # try:
        #     # base.log.debug("updateMessages")
        #
        #     out_ws_par = self.get_parameter_by_name("output_workspace")  # None
        #     out_rasfmt_par = self.get_parameter_by_name("raster_format")  # None
        #
        #     if out_ws_par and out_rasfmt_par:
        #         # base.log.debug("out_ws_par and out_rasfmt_par")
        #
        #         out_ws_par.clearMessage()
        #         out_rasfmt_par.clearMessage()
        #         # base.log.debug("messages cleared")
        #
        #         if out_ws_par.altered or out_rasfmt_par.altered:
        #             # base.log.debug("out_ws_par.altered or out_rasfmt_par.altered")
        #
        #             ws = out_ws_par.value
        #             fmt = out_rasfmt_par.value
        #             # base.log.debug("ws={} fmt={}".format(ws, fmt))
        #             if base.utils.is_local_gdb(ws) and fmt != "Esri Grid":
        #                 out_rasfmt_par.setErrorMessage("Invalid raster format for workspace type")
        # except Exception as e:
        #     # base.log.debug("updateMessages error : {}".format(e))
        #     print str(e)

        # BaseTool.updateMessages(self, parameters)
        # stretch = parameters[2].value == 'STRETCH'
        # if stretch and not parameters[3].valueAsText:
        #     parameters[3].setIDMessage("ERROR", 735, parameters[3].displayName)
        # if stretch and not parameters[4].valueAsText:
        #     parameters[4].setIDMessage("ERROR", 735, parameters[4].displayName)

        return

    @base.log.log
    def execute(self, parameters, messages):
        """ The source code of the tool.

        Args:
            parameters (): The tool parameters
            messages ():  Associated messages

        Returns:

        """
        # check if we have a function to run
        if not self.execution_list:
            raise ValueError("Tool execution list is empty")

        self.arc_messages = messages
        base.log.configure_logging(messages)

        base.log.info("Debugging log file is located at '{}'".format(base.log.LOG_FILE))

        self.parameter_objects = parameters

        [setattr(self, k, v) for k, v in self.get_parameter_dict().iteritems()]
        base.log.debug("Tool attributes set {}".format(self.__dict__))

        if hasattr(self, "result"):
            init = self.result.initialise(self.get_parameter_by_name("result_table"),
                                          self.get_parameter_by_name("fail_table"),
                                          self.get_parameter_by_name("output_workspace").value,
                                          self.get_parameter_by_name("result_table_name").value)
            [base.log.info(x) for x in init]

        # run the functions
        with base.log.error_trap(self):
            for f in self.execution_list:
                if isinstance(f, (list, tuple)):  # expecting to feed a function a function
                    f1, f2 = f  # for now just limit to 2 deep
                    # f1 = base.log.log(f1)
                    # f2 = base.log.log(f2)
                    f1(f2)
                else:  # normal case, expecting a function
                    # f = base.log.log(f)
                    f()

        if hasattr(self, "result"):
            [base.log.info(w) for w in self.result.write()]

        return

    @base.log.log
    def get_parameter_dict(self, leave_as_object=()):
        """ Create a dictionary of parameters

        Args:
            leave_as_object (): A list of parameter names to leave as objects rather than return strings

        Returns: A dictionary of parameters - strings or parameter objects

        """

        # create the dict
        pd = {}
        for p in self.parameter_objects:
            name = p.name
            if name in leave_as_object:
                pd[name] = p
            elif p.dataType == "Boolean":
                pd[name] = [False, True][p.valueAsText == "true"]
            elif p.dataType == "Double":
                pd[name] = float(p.valueAsText)
            elif p.dataType == "Long":
                pd[name] = int(float(p.valueAsText))
            else:
                pd[name] = (p.valueAsText or "#")

        # pd = {p.name: p if p.name in leave_as_object else (p.valueAsText or "#") for p in self.parameter_objects}

        # now fix some specific parameters
        x = pd.get("raster_format", None)
        if x:
            pd["raster_format"] = "" if x.lower() == "esri grid" else '.' + x

        x = pd.get("output_filename_prefix", None)
        if x:
            pd["output_filename_prefix"] = "" if x == "#" else x

        x = pd.get("output_filename_suffix", None)
        if x:
            pd["output_filename_suffix"] = "" if x == "#" else x

        return pd

    @base.log.log
    def get_parameter_names(self):
        """ Create a dictionary of parameter names

        Returns: A dictionary of parameter names

        """

        pn = [p.name for p in self.parameter_objects]

        return pn

    @base.log.log
    def iterate_function_on_tableview(self, func, parameter_name, key_names):
        """ Runs a function over the values in a tableview parameter - a common tool scenario

        Args:
            func (): Function to run
            parameter_name (): Parameter to run on
            key_names (): Fields in the rows to provide

        Returns:

        """
        base.log.debug("locals = {}".format(locals()))

        param = self.get_parameter_by_name(parameter_name)
        if param.datatype != "Table View":
            raise ValueError("That parameter is not a table or table view ({0})".format(param.name))

        multi_val = getattr(param, "multivalue", False)
        if multi_val:
            raise ValueError("Multi value tableview iteration is not yet implemented")

        gg_in_table_text = param.valueAsText

        gg_in_table = "gg_in_table"
        arcpy. MakeTableView_management(gg_in_table_text, gg_in_table)

        gg_in_table_fields = [f.name for f in arcpy.ListFields(gg_in_table)]
        proc_hist_fieldname = "proc_hist"
        if proc_hist_fieldname not in gg_in_table_fields:
            arcpy.AddField_management(gg_in_table, proc_hist_fieldname, "TEXT", None, None, 500000)

        # map fields
        num_fields = len(key_names)  # [rf1, rf2, ...]
        f_names = ["{0}_field_{1}".format(parameter_name, i) for i in range(0, num_fields)]  # [f_0, f_1, ...]
        f_vals = [self.get_parameter_by_name(f_name).valueAsText for f_name in f_names]
        f_vals.append(proc_hist_fieldname)
        rows = [r for r in arcpy.da.SearchCursor(gg_in_table, f_vals)]

        # iterate
        key_names.append(proc_hist_fieldname)
        self.do_iteration(func, rows, key_names)

        return

    @base.log.log
    def iterate_function_on_parameter(self, func, parameter_name, key_names):
        """ Runs a function over the values in a parameter - a less common tool scenario

        Args:
            func (): Function to run
            parameter_name (): Parameter to run on
            key_names (): Fields in the rows to provide

        Returns:

        """

        param = self.get_parameter_by_name(parameter_name)
        multi_val = getattr(param, "multivalue", False)

        if param.datatype == "Table View":
            raise ValueError("Function deprecation, use 'iterate_function_on_tableview'")

        rows = [param.valueAsText.split(";")] if multi_val else [[param.valueAsText]]

        for row in rows:  # add proc_hist field
            row.append("")

        base.log.debug("Processing rows will be {}".format(rows))

        # iterate
        key_names.append("proc_hist")
        self.do_iteration(func, rows, key_names)

        return

    @base.log.log
    def do_iteration(self, func, rows, key_names):

        if not rows:
            raise ValueError("No values or records to process.")

        fname = func.__name__
        base.log.log(func)

        # rows = [utils.make_tuple(row) for row in rows]
        rows = [{k: v for k, v in zip(key_names, utils.make_tuple(row))} for row in rows]
        total_items = len(rows)
        base.log.info("{0} items to process".format(total_items))

        count = 0
        for row in rows:
            try:
                count += 1
                # data = {k: v for k, v in zip(key_names, row)}
                geodata = row.get("geodata", None)
                try:
                    old_proc_hist = row.get("proc_hist", "<History Unknown>")
                    # new_proc_hist = "Tool='{}' Parameters={} Row={}".format(self.label, self.get_parameter_dict(), row)
                    self.result.new_proc_hist = "Tool='{}' Parameters={} Row={}".format(self.label, self.get_parameter_dict(), row)
                except:
                    pass
                base.log.debug("Running {} with data={}".format(fname, row))
                func(row)
            except Exception as e:
                base.log.error("error executing {}: {}".format(fname, str(e)))
                if hasattr(self, "result"):
                    self.result.fail(geodata, row)

        return

    @base.log.log
    def send_info(self, message):
        """ Send an INFO message to user

        DEPRECATED

        Args:
            message (): The message

        Returns:

        """

        self.arc_messages.addMessage("!! self.send_info() is deprecated... use base.log.info() !!")
        if not isinstance(message, list):
            message = [message]

        [self.arc_messages.addMessage(message) for _ in message]

        return

    @base.log.log
    def send_warning(self, message):
        """ Send a WARN message to user

        DEPRECATED

        Args:
            message (): The message

        Returns:

        """

        self.arc_messages.addMessage("!! self.send_warning() is deprecated... use base.log.warn() !!")
        if not isinstance(message, list):
            message = [message]

        [self.arc_messages.addWarningMessage(message) for _ in message]

        return
