# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 10:48:26 2016

@author: byed
"""
from __future__ import print_function
from utils import static_vars, make_tuple, is_local_gdb
from sys import exc_info
from traceback import format_exception
from os import environ, makedirs
from os.path import join, exists
from contextlib import contextmanager
from functools import wraps
import arcpy
import logging
from collections import OrderedDict


def time_stamp(fmt='%Y%m%d_%H%M%S'):
    from datetime import datetime

    return datetime.now().strftime(fmt)


@static_vars(logger=None)
def get_logger():
    if not get_logger.logger:
        get_logger.logger = logging.getLogger("gridgarage")

    return get_logger.logger


def debug(message):
    message = make_tuple(message)

    try:
        logger = get_logger()
        debug_func = logger.debug
    except:
        debug_func = print
        message = ["DEBUG: " + str(msg) for msg in message]

    for msg in message:
        debug_func(msg)

    return


def info(message):
    message = make_tuple(message)

    try:
        logger = get_logger()
        info_func = logger.info
    except:
        info_func = print
        message = ["INFO: " + str(msg) for msg in message]

    for msg in message:
        info_func(msg)

    return


def warn(message):
    message = make_tuple(message)

    try:
        logger = get_logger()
        warn_func = logger.warn
    except:
        warn_func = print
        message = ["WARN: " + str(msg) for msg in message]

    for msg in message:
        warn_func(msg)

    return


def error(message):
    message = make_tuple(message)

    try:
        logger = get_logger()
        error_func = logger.error
    except:
        error_func = print
        message = ["ERROR: " + str(msg) for msg in message]

    for msg in message:
        error_func(msg)

    return


# LOG_FILE = join(APPDATA_PATH, "gridgarage.log")
@contextmanager
def error_trap(context):
    """ A context manager that traps and logs exception in its block.
        Usage:
        with error_trapping('optional description'):
            might_raise_exception()
        this_will_always_be_called()
    """
    # try:
    idx = context.__name__
    # except AttributeError:
    #     idx = inspect.getframeinfo(inspect.currentframe())[2]

    # in_msg = "IN context= " + idx
    # out_msg = "OUT context= " + idx

    try:

        debug("IN context= " + idx)

        yield

        debug("OUT context= " + idx)

    except Exception as e:

        error(repr(format_exception(*exc_info())))

        raise e

    return


def log_error(f):
    """ A decorator to trap and log exceptions """

    @wraps(f)
    def log_wrap(*args, **kwargs):
        with error_trap(f):
            return f(*args, **kwargs)

    return log_wrap


class ArcStreamHandler(logging.StreamHandler):
    """ Logging handler to log messages to ArcGIS """

    def __init__(self, messages):

        logging.StreamHandler.__init__(self)

        self.messages = messages

    def emit(self, record):
        """ Emit the record to the ArcGIS messages object

        Args:
            record (): The message record

        Returns:

        """

        msg = self.format(record)
        msg = msg.replace("\n", ", ").replace("\t", " ").replace("  ", " ")
        lvl = record.levelno

        if lvl in [logging.ERROR, logging.CRITICAL]:
            self.messages.addErrorMessage(msg)

        elif lvl == logging.WARNING:
            self.messages.addWarningMessage(msg)

        else:
            self.messages.addMessage(msg)

        self.flush()

        return


class BaseTool(object):
    def __init__(self, settings):
        print("BaseTool.__init__")

        self.appdata_path = join(environ["USERPROFILE"], "AppData", "Local", "GridGarage")
        self.tool_name = type(self).__name__
        self.time_stamp = time_stamp()
        self.run_id = "{0}_{1}".format(self.tool_name, self.time_stamp)

        self.log_file = join(self.appdata_path, self.tool_name + ".log")
        self.logger = None
        self.debug = debug
        self.info = info
        self.warn = warn
        self.error = error

        self.label = settings.get("label", "label not set")
        self.description = settings.get("description", "description not set")
        self.canRunInBackground = settings.get("can_run_background", False)
        self.category = settings.get("category", False)

        self.parameters = None
        self.messages = None
        self.execution_list = []

        return

    def configure_logging(self):
        print("BaseTool.configure_logging")
        self.messages.addMessage("Initialising logging...")

        logger = get_logger()
        self.debug = logger.debug
        self.info = logger.info
        self.warn = logger.warn
        self.error = logger.error

        logger.handlers = []  # be rid of ones from other tools
        logger.setLevel(logging.DEBUG)

        ah = ArcStreamHandler(self.messages)
        ah.setLevel(logging.INFO)
        logger.addHandler(ah)
        logger.info("ArcMap stream handler configured")

        if not exists(self.log_file):

            if not exists(self.appdata_path):
                logger.info("Creating app data path {}".format(self.appdata_path))
                makedirs(self.appdata_path)

            logger.info("Creating log file {}".format(self.log_file))
            open(self.log_file, 'a').close()

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d %(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s", datefmt="%Y%m%d %H%M%S")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info("File stream handler configured")

        self.logger = logger

        logger.info("Debugging log file is located at '{}'".format(self.log_file))

        return

    @log_error
    def get_parameter(self, param_name, raise_not_found_error=False):

        if self.parameters:

            for param in self.parameters:
                if param.name == param_name:
                    return param

        if raise_not_found_error:
            raise ValueError("Parameter {0} not found".format(param_name))

        return

    def getParameterInfo(self):

        return []

    def isLicensed(self):

        return True

    @log_error
    def updateParameters(self, parameters):

        try:
            ps = [(i, p.name) for i, p in enumerate(parameters)]
            self.debug("BaseTool.updateParameters {}".format(ps))

            # set default result table name

            out_tbl_par = None
            for p in parameters:
                if p.name == "result_table_name":
                    out_tbl_par = p
                    break

            if out_tbl_par and out_tbl_par.value == "#run_id#":
                out_tbl_par.value = self.run_id

            # validate workspace and raster format

            out_ws_par = None
            for p in parameters:
                if p.name == "output_workspace":
                    out_ws_par = p
                    break

            ras_fmt_par = None
            for p in parameters:
                if p.name == "raster_format":
                    ras_fmt_par = p
                    break

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

    @log_error
    def updateMessages(self, parameters):

        self.debug("Well, in here anyway...")
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
        #     # self.debug("messages cleared")
        #
        #     if out_ws_par.altered or ras_fmt_par.altered:
        #         # self.debug("out_ws_par.altered or out_rasfmt_par.altered")
        #
        #         ws = out_ws_par.value
        #         fmt = ras_fmt_par.value
        #         # self.debug("ws={} fmt={}".format(ws, fmt))
        #         if base.utils.is_local_gdb(ws) and fmt != "Esri Grid":
        #             ras_fmt_par.setErrorMessage("Invalid raster format for workspace type")
        # try:
        #     # self.debug("updateMessages")
        #
        #     out_ws_par = self.get_parameter_by_name("output_workspace")  # None
        #     out_rasfmt_par = self.get_parameter_by_name("raster_format")  # None
        #
        #     if out_ws_par and out_rasfmt_par:
        #         # self.debug("out_ws_par and out_rasfmt_par")
        #
        #         out_ws_par.clearMessage()
        #         out_rasfmt_par.clearMessage()
        #         # self.debug("messages cleared")
        #
        #         if out_ws_par.altered or out_rasfmt_par.altered:
        #             # self.debug("out_ws_par.altered or out_rasfmt_par.altered")
        #
        #             ws = out_ws_par.value
        #             fmt = out_rasfmt_par.value
        #             # self.debug("ws={} fmt={}".format(ws, fmt))
        #             if base.utils.is_local_gdb(ws) and fmt != "Esri Grid":
        #                 out_rasfmt_par.setErrorMessage("Invalid raster format for workspace type")
        # except Exception as e:
        #     # self.debug("updateMessages error : {}".format(e))
        #     print str(e)

        # BaseTool.updateMessages(self, parameters)
        # stretch = parameters[2].value == 'STRETCH'
        # if stretch and not parameters[3].valueAsText:
        #     parameters[3].setIDMessage("ERROR", 735, parameters[3].displayName)
        # if stretch and not parameters[4].valueAsText:
        #     parameters[4].setIDMessage("ERROR", 735, parameters[4].displayName)

        return

    @log_error
    def execute(self, parameters, messages):

        if not self.execution_list:
            raise ValueError("Tool execution list is empty")

        self.parameters = parameters
        self.messages = messages

        self.configure_logging()

        parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in self.parameters])
        parameter_summary = ", ".join(["{}: {}".format(k, v) for k, v in parameter_dictionary.iteritems()])
        self.info("Parameter summary: {}".format(parameter_summary))

        for k, v in self.get_parameter_dict().iteritems():
            setattr(self, k, v)

        self.debug("Tool attributes set {}".format(self.__dict__))

        try:
            self.result.initialise(self.get_parameter("result_table"), self.get_parameter("fail_table"), self.get_parameter("output_workspace").value, self.get_parameter("result_table_name").value, self.logger)
        except AttributeError:
            pass

        for f in self.execution_list:
            f = log_error(f)
            f()

        try:
            self.result.write()
        except AttributeError:
            pass

        return

    @log_error
    def get_parameter_dict(self, leave_as_object=()):
        """ Create a dictionary of parameters

        Args:
            leave_as_object (): A list of parameter names to leave as objects rather than return strings

        Returns: A dictionary of parameters - strings or parameter objects

        """

        # create the dict
        # TODO make multivalue parameters a list
        # TODO see what binning the bloody '#' does to tools
        pd = {}
        for p in self.parameters:
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
            v = pd.get(p, None)
            if v:
                pd[p] = "" if v == "#" else v
            return

        set_hash_to_empty("output_filename_prefix")
        set_hash_to_empty("output_filename_suffix")

        return pd

    @log_error
    def iterate_function_on_tableview(self, func, parameter_name, key_names, nonkey_names=None, return_to_results=False):
        """ Runs a function over the values in a tableview parameter - a common tool scenario

        Args:
            func (): Function to run
            parameter_name (): Parameter to run on
            key_names (): Fields in the rows to provide

        Returns:

        """
        self.debug("locals = {}".format(locals()))

        param = self.get_parameter(parameter_name)
        if param.datatype != "Table View":
            raise ValueError("That parameter is not a table or table view ({0})".format(param.name))

        multi_val = getattr(param, "multiValue", False)
        if multi_val:
            raise ValueError("Multi-value tableview iteration is not yet implemented")

        gg_in_table_text = param.valueAsText

        gg_in_table = "gg_in_table"
        if arcpy.Exists(gg_in_table):
            arcpy.Delete_management(gg_in_table)
        arcpy.MakeTableView_management(gg_in_table_text, gg_in_table)

        gg_in_table_fields = [f.name for f in arcpy.ListFields(gg_in_table)]

        # map fields
        num_fields = len(key_names)  # [rf1, rf2, ...]
        f_names = ["{0}_field_{1}".format(parameter_name, k) for k in key_names]  # [f_0, f_1, ...]
        f_vals = [self.get_parameter(f_name).valueAsText for f_name in f_names]
        if nonkey_names:
            f_vals.extend(nonkey_names)
        rows = [r for r in arcpy.da.SearchCursor(gg_in_table, f_vals)]

        # iterate
        if nonkey_names:
            key_names.extend(nonkey_names)

        self.do_iteration(func, rows, key_names, return_to_results)

        return

    @log_error
    def iterate_function_on_parameter(self, func, parameter_name, key_names, nonkey_names=None, return_to_results=False):
        """ Runs a function over the values in a parameter - a less common tool scenario

        Args:
            func (): Function to run
            parameter_name (): Parameter to run on
            key_names (): Fields in the rows to provide

        Returns:

        """

        param = self.get_parameter(parameter_name)
        multi_val = getattr(param, "multiValue", False)
        self.debug("multiValue attribute is {}".format(multi_val))

        if param.datatype == "Table View":
            raise ValueError("No, use 'iterate_function_on_tableview'")

        self.debug("param.valueAsText =  {}".format(param.valueAsText))
        self.debug("param.valueAsText.split(';' =  {}".format(param.valueAsText.split(";")))
        rows = param.valueAsText.split(";") if multi_val else [param.valueAsText]

        self.debug("Processing rows will be {}".format(rows))

        # iterate
        if nonkey_names:
            key_names.extend(nonkey_names)

        self.do_iteration(func, rows, key_names, return_to_results)

        return

    @log_error
    def do_iteration(self, func, rows, key_names, return_to_results):

        if not rows:
            raise ValueError("No values or records to process.")

        fname = func.__name__
        func = log_error(func)

        rows = [{k: v for k, v in zip(key_names, make_tuple(row))} for row in rows]
        total_rows = len(rows)
        self.info("{} items to process".format(total_rows))
        row_num = 0
        # try:
        #     add = log_error(self.result.add_pass)
        # except AttributeError:
        #     pass

        for row in rows:
            try:
                # try:
                #     self.result.new_proc_hist = "To be deprecated"  # "Tool='{}' Parameters={} Row={}".format(self.label, self.get_parameter_dict(), row)
                # except AttributeError:
                #     pass

                row_num += 1
                self.info("{} > Processing row {} of {}".format(time_stamp("%H:%M:%S%f")[:-3], row_num, total_rows))
                self.debug("Running {} with row={}".format(fname, row))
                res = func(row)
                if return_to_results:
                    try:
                        self.result.add_pass(res)
                    except AttributeError:
                        raise ValueError("No result attribute for result record")

            except Exception as e:

                self.error("error executing {}: {}".format(fname, str(e)))

                try:
                    fail = log_error(self.result.add_fail)
                    fail(row)
                except AttributeError:
                    pass

        return
