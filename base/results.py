# import base.geodata import describe_arc, table_conversion
import base.utils
import shutil
import os
import csv
import traceback
import sys
import base.log


def result(cls):
    setattr(cls, "result", ResultsUtils())
    return cls


class ResultsUtils(object):
    @base.log.log
    def __init__(self):
        """ Add class members """

        self.fail_table = ""
        self.fail_table_name = ""
        self.fail_count = 0
        self.fail_table_output_parameter = None
        self.fail_csv = ""

        self.result_table = ""
        self.result_table_name = ""
        self.result_count = 0
        self.result_table_output_parameter = None
        self.result_csv = ""

        self.output_workspace = ""
        self.output_workspace_type = ""
        self.output_workspace_parent = ""

        return

    @base.log.log
    def initialise(self, result_table_param, fail_table_param, out_workspace, result_table_name):
        """ Initialise the results for the instance

        Args:
            result_table_param (): Tool result table parameter
            fail_table_param ():  Tool fail table parameter
            out_workspace (): Output workspace
            result_table_name (): Base name of result table

        Returns: A list of strings reflection operations

        """

        self.result_table_output_parameter = result_table_param
        self.fail_table_output_parameter = fail_table_param

        self.output_workspace = out_workspace.value
        self.output_workspace_type = base.utils.describe_arc(self.output_workspace).workspaceType

        self.output_workspace_parent = os.path.split(self.output_workspace)[0]

        if self.output_workspace_type == "RemoteDatabase":
            e = ValueError("Remote database workspaces are not yet supported")
            base.log.debug(e)
            raise e

        # if output is to a fgdb, put the csv into it's parent folder
        csv_ws = self.output_workspace_parent if self.output_workspace_type == "LocalDatabase" else self.output_workspace

        tn = result_table_name
        if tn:
            self.result_table_name = tn
            self.fail_table_name = tn + "_FAIL"
            self.result_table = os.path.join(self.output_workspace, tn)
            self.fail_table = self.result_table + "_FAIL"
            self.result_csv = os.path.join(csv_ws, tn + ".csv")
            self.fail_csv = os.path.join(csv_ws, tn + "_FAIL.csv")

        ret = []
        try:
            os.remove(self.result_csv)
            ret.append("Existing results csv at {} removed".format(self.result_csv))
        except:
            pass
        try:
            os.remove(self.fail_csv)
            ret.append("Existing fail csv at {} removed".format(self.fail_csv))
        except:
            pass

        if self.output_workspace_type == "LocalDatabase":
            ret.append("Temporary Results initialised:")
        else:
            ret.append("Results initialised:")

        ret.append("Result CSV @ {}".format(self.result_csv))
        ret.append("Failure CSV @ {}".format(self.fail_csv))

        return ret

    @base.log.log
    def add(self, result):
        """ Write result record to CSV

        Writes a result to the temp CSV immediately, trade off between
        runtime performance, RAM usage and FAILURE (i.e. recovery of results)

        Args:
            result ():

        Returns:

        """

        base.log.debug("ResultsUtils.add result={}".format(result))

        if not result:  # in case a caller passes in None or []
            return "Result was empty"

        if not self.result_csv:
            raise ValueError("Result CSV is not set")

        # work out if we have a single or multiple results
        is_tuple = isinstance(result, (tuple, list))

        # here we will just store the keys from the first result,
        # re-using these will force an error for any inconsistency
        # write the header on first call
        if not os.path.isfile(self.result_csv):
            result_fieldnames = result[0].keys() if is_tuple else result.keys()
            result_fieldnames.append("proc_hist")
            setattr(self, "result_fieldnames", result_fieldnames)
            with open(self.result_csv, "wb") as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', fieldnames=self.result_fieldnames)
                writer.writeheader()

        # write the data
        with open(self.result_csv, "ab") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.result_fieldnames)
            if is_tuple:

                for r in result:  # add proc_hist data
                    geodata = r.get("geodata", "geodata not set")
                    source_geodata = r.get("source_geodata", "source not set")
                    proc_hist = getattr(self, "new_proc_hist", "proc_hist not set")
                    r["proc_hist"] = "{} << {} << {}".format(geodata, proc_hist, source_geodata)

                writer.writerows(result)
                self.result_count += len(result)
            else:
                geodata = result.get("geodata", "geodata not set")
                source_geodata = result.get("source_geodata", "source not set")
                proc_hist = getattr(self, "new_proc_hist", "proc_hist not set")
                result["proc_hist"] = "{} << {} << {}".format(geodata, proc_hist, source_geodata)

                writer.writerow(result)
                self.result_count += 1

        result = "Result written: {}".format(result)

        return result

    @base.log.log
    def fail(self, geodata, row):
        """ Write failure record to CSV

        Writes a failure to the temp CSV immediately, trade off between
        runtime performance, RAM usage and FAILURE (i.e. recovery of results)

        Args:
            geodata ():
            row ():

        Returns:

        """

        if not self.fail_csv:
            raise ValueError("Fail CSV is not set")

        # write the header on first call
        if not os.path.isfile(self.fail_csv):
            setattr(self, "failure_fieldnames", ["geodata", "failure", "row_data"])
            with open(self.fail_csv, "wb") as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', fieldnames=self.failure_fieldnames)
                writer.writeheader()

        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        msg = tbinfo + str(sys.exc_info()[1])
        msg = msg.strip().replace('\n', ', ').replace('\r', ' ').replace('  ', ' ')

        geodata = row.get("geodata", "geodata not set")
        source_geodata = row.get("source_geodata", "source not set")
        proc_hist = getattr(self, "new_proc_hist", "proc_hist not set")
        row["proc_hist"] = "{} << {} << {}".format(geodata, proc_hist, source_geodata)

        # write the failure record
        with open(self.fail_csv, "ab") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.failure_fieldnames)
            writer.writerow({"geodata": geodata, "failure": msg, "row_data": str(row)})
            self.fail_count += 1

        return

    @base.log.log
    def write(self):
        """ Write the success and failure csv files to the final tables

        Returns: A list of strings reflecting operation results

        """
        ret = self._write_results() + self._write_failures()

        return ret

    @base.log.log
    def _write_results(self):
        """ Write the result CSV rows to the final table

        Returns: A list of strings reflecting operation status

        """
        msg = []

        if not os.path.exists(self.result_csv):
            msg.append("No results")
        else:
            if self.output_workspace_type == "LocalDatabase":  # it's an fgdb
                try:
                    self.result_table = base.utils.table_conversion(self.result_csv, self.output_workspace, self.result_table_name)
                    os.remove(self.result_csv)
                except:
                    self.result_table = os.path.join(self.output_workspace_parent, self.result_table_name + ".csv")
                    shutil.copyfile(self.result_csv, self.result_table)
                    os.remove(self.result_csv)
                    err_msg = "Table to Table Conversion failed. Hoisted temporary result CSV to database parent directory...\n"
            else:  # it's a directory
                self.result_table = self.result_csv

            self.result_table_output_parameter.value = self.result_table
            msg.append("Final results at {0}".format(self.result_table))

        return msg

    @base.log.log
    def _write_failures(self):
        """ Write the failure CSV rows to the final table

        Returns: A list of strings reflecting operation status

        """

        err_msg = []

        if not os.path.exists(self.fail_csv) or not self.fail_count:
            err_msg.append("No failures")
        else:
            if self.output_workspace_type != "FileSystem":  # it's a a fgdb or rmdb
                try:
                    self.fail_table = base.utils.table_conversion(self.fail_csv, self.output_workspace, self.fail_table_name)
                    os.remove(self.fail_csv)
                except:
                    self.fail_table = os.path.join(self.output_workspace_parent, self.fail_table_name + ".csv")
                    shutil.copyfile(self.fail_csv, self.fail_table)
                    os.remove(self.fail_csv)
                    err_msg.append("Table to Table Conversion failed. Hoisted temporary failure CSV to database parent directory...")
            else:
                self.fail_table = self.fail_csv

            self.fail_table_output_parameter.value = self.fail_table
            err_msg.append("Failures at {0}".format(self.fail_table))

        return err_msg

# this message based status thing above is pretty dodgy needs to be reworked sensibly, just a messy job to refactor as now interwoven through most tools
