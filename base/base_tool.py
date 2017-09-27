# -*- coding: utf-8 -*-
"""
Description
-----------
    This module provides a base tool class for Grid Garage tools

Author
------
    D.Bye, NSW OEH EMS KST

**Ecosystem Management Science**

**Knowledge Services Team**

Implementation
--------------
"""

from __future__ import print_function
from utils import make_tuple, is_local_gdb
from sys import exc_info
from traceback import format_exception
from os import environ, makedirs
from os.path import join, exists
from contextlib import contextmanager
from functools import wraps
import arcpy
import logging
from base.results import GgResult
from datetime import datetime


debug = print  # updated to logger.debug after logging is configured


def time_stamp(fmt='%Y%m%d_%H%M%S'):
    """Return the current date-time as a formatted string

    Args:
        fmt (string): Date-time format

    Returns:
        string: Formatted timestamp
    """

    return datetime.now().strftime(fmt)


@contextmanager
def error_trap(context):
    """A context manager that traps and logs exception in its block

    Args:
        context (function): function to be contextualised

    Returns:
        :

    Raises:
        caught (exception): original exception is re-raised after debug logging
    """

    idx = context.__name__

    try:

        debug("IN: " + idx)

        yield

        debug("OUT: " + idx)

    except Exception as e:

        debug(repr(format_exception(*exc_info())))

        raise e

    return


def log_error(f):
    """A decorator to trap and log exceptions

    Args:
        f (function): Target function

    Returns:
        function: Wrapped function
    """

    @wraps(f)
    def log_wrap(*args, **kwargs):
        """ Wrapping function

        Args:
            args:
            kwargs:

        Returns:
            wrapped (function)

        """
        with error_trap(f):
            return f(*args, **kwargs)

    return log_wrap


class ArcStreamHandler(logging.StreamHandler):
    """  Logging handler to send messages to ArcGIS tool window
    """

    def __init__(self, messages):
        """

        Args:
            messages (object): ArcGIS tool messages object
        """

        logging.StreamHandler.__init__(self)

        self.messages = messages

    def emit(self, record):
        """Emit the record to the ArcGIS messages object

        Args:
            record:

        Returns:
            :
        """

        msg = self.format(record).replace("\n", ", ").replace("\t", " ").replace("  ", " ")

        lvl = record.levelno

        if self.messages:

            if lvl in [logging.ERROR, logging.CRITICAL]:
                self.messages.addErrorMessage(msg)

            elif lvl == logging.WARNING:
                self.messages.addWarningMessage(msg)

            else:
                self.messages.addMessage(msg)

        self.flush()

        return


class BaseTool(object):
    """ Tool base class
    """
    def __init__(self, settings):
        """Add basic attributes and customise tool parameters from settings

        Args:
            settings (dictionary): name/value pairs
        Returns:
            :
        """
        debug("BaseTool.__init__")

        # instance id attributes
        self.appdata_path = join(environ["USERPROFILE"], "AppData", "Local", "GridGarage")
        self.tool_name = type(self).__name__
        self.time_stamp = time_stamp()
        self.run_id = "{0}_{1}".format(self.tool_name, self.time_stamp)

        # logging attributes
        self.log_file = join(self.appdata_path, self.tool_name + ".log")
        self.logger = None
        self.debug = None
        self.info = None
        self.warn = None
        self.error = None

        # basic tool settings
        self.label = settings.get("label", "label not set")
        self.description = settings.get("description", "description not set")
        self.canRunInBackground = settings.get("can_run_background", False)
        self.category = settings.get("category", False)

        # refs to arc parameters
        self.parameters = None
        self.messages = None

        # other attributes
        self.execution_list = []
        self.result = GgResult()

        return

    def configure_logging(self):
        """ Configure the logging module for the tool

        Returns:
            :
        """
        global debug  # may be mutated

        debug("configure_logging")

        if not self.messages:  # EARLY EXIT
            debug("messages not set")
            return
        else:
            self.messages.addMessage("Initialising logging...")

        logger = logging.getLogger(self.tool_name)

        # convenience aliases
        self.debug = logger.debug
        self.info = logger.info
        self.warn = logger.warn
        self.error = logger.error

        # replace debug (print) with the logger function, s
        # sometimes handy to have this available before logging is properly configured
        debug = self.debug

        logger.setLevel(logging.DEBUG)

        # add the ArcMap stream handler
        ah = ArcStreamHandler(self.messages)
        ah.setLevel(logging.INFO)
        logger.addHandler(ah)
        logger.info("ArcMap stream handler configured")

        # create log file if necessary
        if not exists(self.log_file):

            if not exists(self.appdata_path):

                logger.info("Creating app data path {}".format(self.appdata_path))
                makedirs(self.appdata_path)

            logger.info("Creating log file {}".format(self.log_file))
            open(self.log_file, 'a').close()

        # add the file stream handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d %(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s", datefmt="%Y%m%d %H%M%S")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info("File stream handler configured")

        # convenience alias
        self.logger = logger
        logger.info("Debugging log file is located at '{}'".format(self.log_file))

        return

    def get_parameter(self, param_name, raise_not_found_error=False, parameters=None):
        """ Return an input parameter based on the parameter name

        Args:
            param_name (str): Name of parameter
            raise_not_found_error (boolean): Flag for raising an error if parameter name is not found
            parameters (list): parameters as list of objects

        Returns:
            :
        """

        if not parameters:  # nothing passed in
            parameters = self.parameters  # so use stored value

        try:
            param = self.get_parameter_dict(leave_as_object=param_name, parameters=parameters)[param_name]

        except KeyError:

            if raise_not_found_error:
                raise ValueError("Parameter '{}' not found".format(param_name))

            else:
                return None

        return param

    def getParameterInfo(self):
        """ See ESRI docs

        Returns:

        """

        return []

    def isLicensed(self):
        """ See ESRI docs

        Returns:

        """

        return True

    def updateParameters(self, parameters):
        """ See ESRI docs

        Args:
            parameters:

        Returns:

        """

        try:
            # set default result table name
            out_tbl_par = None
            for p in parameters:
                if p.name == "result_table_name":
                    out_tbl_par = p
                    break

            if out_tbl_par and out_tbl_par.value == "#run_id#":
                out_tbl_par.value = self.run_id

            # validate workspace and raster format
            out_ws_par = self.get_parameter("output_workspace", raise_not_found_error=False)
            ras_fmt_par = self.get_parameter("raster_format", raise_not_found_error=False)

            if out_ws_par and ras_fmt_par:

                out_ws_par.clearMessage()
                ras_fmt_par.clearMessage()

                if out_ws_par.altered or ras_fmt_par.altered:

                    ws = out_ws_par.value
                    fmt = ras_fmt_par.value

                    if is_local_gdb(ws) and fmt != "Esri Grid":
                        ras_fmt_par.setErrorMessage("Invalid raster format for workspace type")
        except:
            pass

        return

    # def updateMessages(self, parameters):
    #     """
    #
    #     Args:
    #         parameters:
    #
    #     Returns:
    #
    #     """
    #
    #     debug("updateMessages exposure code")
    #     # out_ws_par = None
    #     # for p in parameters:
    #     #     if p.name == "output_workspace":
    #     #         out_ws_par = p
    #     #         break
    #     #
    #     # ras_fmt_par = None
    #     # for p in parameters:
    #     #     if p.name == "raster_format":
    #     #         ras_fmt_par = p
    #     #         break
    #     #
    #     # if out_ws_par and ras_fmt_par:
    #     #
    #     #     out_ws_par.clearMessage()
    #     #     ras_fmt_par.clearMessage()
    #     #     # self.debug("messages cleared")
    #     #
    #     #     if out_ws_par.altered or ras_fmt_par.altered:
    #     #         # self.debug("out_ws_par.altered or out_rasfmt_par.altered")
    #     #
    #     #         ws = out_ws_par.value
    #     #         fmt = ras_fmt_par.value
    #     #         # self.debug("ws={} fmt={}".format(ws, fmt))
    #     #         if base.utils.is_local_gdb(ws) and fmt != "Esri Grid":
    #     #             ras_fmt_par.setErrorMessage("Invalid raster format for workspace type")
    #     # try:
    #     #     # self.debug("updateMessages")
    #     #
    #     #     out_ws_par = self.get_parameter_by_name("output_workspace")  # None
    #     #     out_rasfmt_par = self.get_parameter_by_name("raster_format")  # None
    #     #
    #     #     if out_ws_par and out_rasfmt_par:
    #     #         # self.debug("out_ws_par and out_rasfmt_par")
    #     #
    #     #         out_ws_par.clearMessage()
    #     #         out_rasfmt_par.clearMessage()
    #     #         # self.debug("messages cleared")
    #     #
    #     #         if out_ws_par.altered or out_rasfmt_par.altered:
    #     #             # self.debug("out_ws_par.altered or out_rasfmt_par.altered")
    #     #
    #     #             ws = out_ws_par.value
    #     #             fmt = out_rasfmt_par.value
    #     #             # self.debug("ws={} fmt={}".format(ws, fmt))
    #     #             if base.utils.is_local_gdb(ws) and fmt != "Esri Grid":
    #     #                 out_rasfmt_par.setErrorMessage("Invalid raster format for workspace type")
    #     # except Exception as e:
    #     #     # self.debug("updateMessages error : {}".format(e))
    #     #     print str(e)
    #
    #     # BaseTool.updateMessages(self, parameters)
    #     # stretch = parameters[2].value == 'STRETCH'
    #     # if stretch and not parameters[3].valueAsText:
    #     #     parameters[3].setIDMessage("ERROR", 735, parameters[3].displayName)
    #     # if stretch and not parameters[4].valueAsText:
    #     #     parameters[4].setIDMessage("ERROR", 735, parameters[4].displayName)
    #
    #     return

    @log_error
    def execute(self, parameters, messages):
        """  See ESRI docs, tool execution, called by ArcGIS

        Args:
            parameters (list): parameter objects
            messages (object): messages object

        Returns:
            :
        """

        if not self.execution_list:
            raise ValueError("Tool execution list is empty")

        # hold for later ref
        self.parameters = parameters
        self.messages = messages

        self.configure_logging()

        if not self.messages:  # stop run errors during ide tests
            return

        self.info("Parameter summary: {}".format(["{} ({}): {}".format(p.DisplayName, p.name, p.valueAsText) for p in self.parameters]))

        # set the input parameters as local attributes
        [setattr(self, k, v) for k, v in self.get_parameter_dict().iteritems()]  # nb side-effect
        self.debug("Tool attributes set {}".format(self.__dict__))

        # try:
        self.result.initialise(self.get_parameter("result_table"), self.get_parameter("fail_table"), self.get_parameter("output_workspace").value, self.get_parameter("result_table_name").value, self.logger)

        # except AttributeError:
        #     pass

        try:
            if self.output_file_workspace in [None, "", "#"]:
                self.output_file_workspace = self.result.output_workspace

        except AttributeError:
            pass

        for f in self.execution_list:
            f = log_error(f)
            f()

        try:
            self.result.write()

        except TypeError:
            pass

        return

    def get_parameter_dict(self, leave_as_object=(), parameters=()):
        """ Return an input parameter name:object dictionary

        Args:
            leave_as_object (list): Names of input parameters to leave as objects rather than use string representation
            parameters (list): Input parameters

        Returns:
            :
        """

        # create the dict
        if not parameters:
            parameters = self.parameters

        pd = {}
        for p in parameters:
            name = p.name
            if name in leave_as_object:
                pd[name] = p
            elif p.datatype == "Boolean":
                pd[name] = [False, True][p.valueAsText == "true"]
            elif p.datatype == "Double":
                pd[name] = float(p.valueAsText) if p.valueAsText else None
            elif p.datatype == "Long":
                pd[name] = int(float(p.valueAsText)) if p.valueAsText else None
            else:
                pd[name] = p.valueAsText or "#"

        # now fix some specific parameters
        x = pd.get("raster_format", None)
        if x:
            pd["raster_format"] = "" if x.lower() == "esri grid" else '.' + x

        def set_hash_to_empty(p):
            """ Set any string '#' to '' (empty)

            Args:
                p (list): parameters as dictionary

            Returns:
                pd (dict): modified parameters
            """
            v = pd.get(p, None)
            if v:
                pd[p] = "" if v == "#" else v
            return

        set_hash_to_empty("output_filename_prefix")
        set_hash_to_empty("output_filename_suffix")

        return pd

    def iterate_function_on_tableview(self, func, tableview_parameter_name="", nonkey_names=[], return_to_results=False):
        """Runs a function over the values in a tableview parameter - a common tool scenario

        Args:
            func (function): Function to be called iteratively
            tableview_parameter_name (string): The name of the tableview input parameter
            nonkey_names (list): other fields to include
            return_to_results (boolean): Flag for automatically adding the return value to the result

        Returns:
            :
        """

        self.debug("locals = {}".format(locals()))

        # if name keyword is not supplied, use the first parameter in the list
        param = self.get_parameter(tableview_parameter_name) if tableview_parameter_name else self.parameters[0]

        # validate parameter type - must be Table View
        if param.datatype != "Table View":
            raise ValueError("That parameter is not a table or table view ({0})".format(param.name))

        # validate parameter multiValue attribute - must be False
        if getattr(param, "multiValue", False):
            raise ValueError("Multi-value tableview iteration is not yet implemented")

        # ensure nothing left over, sometimes slow gc needs this
        if arcpy.Exists(param.name):
            arcpy.Delete_management(param.name)

        arcpy.MakeTableView_management(param.valueAsText, param.name)

        # this code is difficult to make any clearer, builds a dict of name/alias pairs for parameters
        f_alias = [p.name for i, p in enumerate(self.parameters[1:]) if 0 in p.parameterDependencies]
        f_name = [self.get_parameter(f_name).valueAsText for f_name in f_alias]
        alias_name = {k: v for k, v in dict(zip(f_alias, f_name)).iteritems() if v not in [None, "NONE"]}

        if nonkey_names:  # we want hard-wired fields to be included in the row
            alias_name.update({v: v for v in nonkey_names})  # nonkey_names is a list at the mo

        rows = [r for r in arcpy.da.SearchCursor(param.name, alias_name.values())]

        self.do_iteration(func, rows, alias_name, return_to_results)

        return

    def iterate_function_on_parameter(self, func, parameter_name, key_names, return_to_results=False):
        """Runs a function over the values in a parameter - a less common tool scenario

        Args:
            func (): Function to run
            parameter_name (): Parameter to run on
            key_names (): Fields in the rows to provide
            return_to_results (boolean): Flag for automatically adding the return value to the result

        Returns:
            :
        """

        param = self.get_parameter(parameter_name)
        multi_val = getattr(param, "multiValue", False)

        self.debug("multiValue attribute is {}".format(multi_val))

        # validate parameter type - must NOT be Table View, we have special code for that
        if param.datatype == "Table View":
            raise ValueError("No, use 'iterate_function_on_tableview'")

        self.debug("param.valueAsText =  {}".format(param.valueAsText))
        self.debug("param.valueAsText.split(';' =  {}".format(param.valueAsText.split(";")))

        # create list from mv parameter
        rows = param.valueAsText.split(";") if multi_val else [param.valueAsText]

        self.debug("Processing rows will be {}".format(rows))

        key_names = {v: v for v in key_names}

        self.do_iteration(func, rows, key_names, return_to_results)

        return

    def do_iteration(self, func, rows, name_vals, return_to_results):
        """ Iterates a function over the provided rows

        The function is usually defined in descendant classes, which can
        assume that the function is called for each row in the input table

        Args:
            func (function):
            rows (list):
            name_vals (list):
            return_to_results (boolean): Flag indicating if returned object should be passed on as a result record

        Returns:
            :
        """

        if not rows:
            raise ValueError("No values or records to process.")

        fname = func.__name__

        rows = [{k: v for k, v in zip(name_vals.keys(), make_tuple(row))} for row in rows]
        total_rows = len(rows)
        self.info("{} items to process".format(total_rows))

        for row_num, row in enumerate(rows, start=1):
            try:
                self.info("{} > Processing row {} of {}".format(time_stamp("%H:%M:%S%f")[:-3], row_num, total_rows))
                self.debug("Running {} with row={}".format(fname, row))

                res = func(row)

                if return_to_results:

                    self.result.add_pass(res)

            except Exception as e:

                self.error("error executing {}: {}".format(fname, str(e)))
                self.result.add_fail(row)

        return
