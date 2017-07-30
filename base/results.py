from base.utils import make_tuple
from arcpy import Describe, TableToTable_conversion, FieldMappings, FieldMap, Field
# from shutil import copyfile
from sys import exc_info
from traceback import format_exception
import os
import csv


def result(cls):
    setattr(cls, "result", ResultsUtils())
    return cls


class ResultsUtils(object):

    def __init__(self):
        """ Add class members """

        self.fail_table = ""
        self.fail_table_name = ""
        self.fail_count = 0
        self.fail_table_output_parameter = None
        self.fail_csv = ""

        self.pass_table = ""
        self.pass_table_name = ""
        self.pass_count = 0
        self.pass_table_output_parameter = None
        self.pass_csv = ""

        self.output_workspace = ""
        self.output_workspace_type = ""
        self.output_workspace_parent = ""

        self.logger = None

        return

    def initialise(self, result_table_param, fail_table_param, out_workspace, result_table_name, logger):
        """ Initialise the results for the instance

        Args:
            result_table_param (): Tool result table parameter
            fail_table_param ():  Tool fail table parameter
            out_workspace (): Output workspace
            result_table_name (): Base name of result table
            logger (): 

        Returns:

        """

        self.logger = logger
        logger.info("Initialising result files...")

        self.pass_table_output_parameter = result_table_param
        self.fail_table_output_parameter = fail_table_param

        self.output_workspace = out_workspace.value
        self.output_workspace_type = Describe(self.output_workspace).workspaceType

        self.output_workspace_parent = os.path.split(self.output_workspace)[0]

        if self.output_workspace_type == "RemoteDatabase":

            raise ValueError("Remote database workspaces are not yet supported")

        # if output is to a fgdb, put the csv into it's parent folder
        csv_ws = self.output_workspace_parent if self.output_workspace_type == "LocalDatabase" else self.output_workspace

        tn = result_table_name
        if tn:
            self.pass_table_name = tn
            self.pass_table = os.path.join(self.output_workspace, self.pass_table_name)
            self.pass_csv = os.path.join(csv_ws, tn + ".csv")

            self.fail_table_name = tn + "_FAIL"
            self.fail_table = os.path.join(self.output_workspace, self.fail_table_name)
            self.fail_csv = os.path.join(csv_ws, tn + "_FAIL.csv")

        try:
            os.remove(self.pass_csv)
            logger.info("Existing results csv at {} removed".format(self.pass_csv))
        except:
            pass
        try:
            os.remove(self.fail_csv)
            logger.info("Existing fail csv at {} removed".format(self.fail_csv))
        except:
            pass

        tmp_str = "Temporary " if self.output_workspace_type == "LocalDatabase" else ""
        pass_msg = ("{}Result CSV initialised: {}".format(tmp_str, self.pass_csv))
        fail_msg = ("{}Failure CSV initialised: {}".format(tmp_str, self.fail_csv))

        logger.debug(locals())
        logger.info(pass_msg)
        logger.info(fail_msg)

        return

    def add_pass(self, results):
        """ Write result record to CSV

        Writes a result to the temp CSV immediately, trade off between
        runtime performance, RAM usage and FAILURE (i.e. recovery of results)

        Args:
            results ():

        Returns:

        """

        if not results:  # in case a caller passes in None or []
            self.logger.warn("Result was empty")

        if not self.pass_csv:
            raise ValueError("Result CSV '{}' is not set".format(self.pass_csv))

        results = make_tuple(results)

        # here we will just store the keys from the first result, re-using these will force an error for any inconsistency
        if not os.path.isfile(self.pass_csv):
            result_fieldnames = results[0].keys()
            setattr(self, "result_fieldnames", result_fieldnames)
            with open(self.pass_csv, "wb") as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', fieldnames=self.result_fieldnames)
                writer.writeheader()  # write the header on first call
            self.logger.info("Header written to '{}".format(self.pass_csv))

        # write the data
        with open(self.pass_csv, "ab") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.result_fieldnames)
            writer.writerows(results)
            self.pass_count += len(results)

        self.logger.info("Result written: {}".format(results))

        return

    def add_fail(self, row):
        """ Write failure record to CSV

        Writes a failure to the temp CSV immediately, trade off between
        runtime performance, RAM usage and FAILURE (i.e. recovery of results)

        Args:
            geodata ():
            row ():

        Returns:

        """

        if not row:  # in case a caller passes in None or []
            self.logger.warn("Fail row was empty")

        if not self.fail_csv:
            raise ValueError("Fail CSV '{}' is not set".format(self.fail_csv))

        # write the header on first call
        if not os.path.isfile(self.fail_csv):
            setattr(self, "failure_fieldnames", ["geodata", "failure", "row_data"])
            with open(self.fail_csv, "wb") as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', fieldnames=self.failure_fieldnames)
                writer.writeheader()

        # tb = exc_info()[2]
        # tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        msg = repr(format_exception(*exc_info()))
        # tbinfo + str(exc_info()[1])
        msg = msg.strip().replace('\n', ', ').replace('\r', ' ').replace('  ', ' ')

        try:
            geodata = row["raster"]
        except KeyError:
            try:
                geodata = row["feature"]
            except KeyError:
                try:
                    geodata = row["geodata"]
                except KeyError:
                    geodata = "geodata not set for row"

        # write the failure record
        with open(self.fail_csv, "ab") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.failure_fieldnames)
            writer.writerow({"geodata": geodata, "failure": msg, "row_data": str(row)})
            self.fail_count += 1

        self.logger.info("Fail written: {}".format(msg))

        return

    def write(self):
        """ Write the success and failure csv files to the final tables """

        self._write_results()
        self._write_failures()

        return

    def _write_results(self):
        """ Write the result CSV rows to the final table """

        if not os.path.exists(self.pass_csv):
            self.logger.warn("No results")

            return

        if self.output_workspace_type == "LocalDatabase":  # it's an fgdb
            try:
                self.pass_table = self.table_conversion(self.pass_csv, self.output_workspace, self.pass_table_name)
                os.remove(self.pass_csv)
            except Exception as e:
                self.logger.warn("Table conversion failed: {}".format(e))
                self.pass_table = self.pass_csv
                self.logger.warn("Result as CSV here: '{}'".format(self.pass_csv))
        else:  # it's a directory
            self.pass_table = self.pass_csv

        self.pass_table_output_parameter.value = self.pass_table

        self.logger.debug(self.__dict__)
        self.logger.info("Final results at {}".format(self.pass_table))

        return

    def _write_failures(self):
        """ Write the failure CSV rows to the final table """

        if not os.path.exists(self.fail_csv) or not self.fail_count:
            self.logger.info("No failures")

            return

        if self.output_workspace_type != "FileSystem":  # it's a a fgdb or rmdb
            try:
                self.fail_table = self.table_conversion(self.fail_csv, self.output_workspace, self.fail_table_name)
                os.remove(self.fail_csv)
            except Exception as e:
                self.logger.warn("Table conversion failed: {}".format(e))
                self.fail_table = self.fail_csv
                self.logger.warn("Failures as CSV here: '{}'".format(self.fail_csv))
        else:
            self.fail_table = self.fail_csv

        self.fail_table_output_parameter.value = self.fail_table

        self.logger.debug(self.__dict__)
        self.logger.info("Failures at {}".format(self.fail_table))

        return

    def table_conversion(self, in_rows, out_path, out_name):
        """ Copy a file-based table to a local database, returns full path to new table if successful"""

        out_name_full = os.path.join(out_path, out_name)
        self.logger.info("Converting {} --> {}".format(in_rows, out_name_full))

        fms = FieldMappings()
        fms.addTable(in_rows)

        # this code does not work as planned but has unexpected side effects...
        # it makes the fields size themselves properly!
        for i, f in enumerate(fms):
            fm = fms.getFieldMap(i)
            # fm2 = FieldMap()
            f = Field()
            f.name = fm.outputField.name
            f.type = "String"
            f.length = 8000
            fm.outputField = f
            fms.replaceFieldMap(i, fm)
            # self.logger.info("{} type {} length is {}".format(fm.outputField.name, fm.outputField.type, fm.outputField.length))

        TableToTable_conversion(in_rows, out_path, out_name, None, fms, None)

        return out_name_full

