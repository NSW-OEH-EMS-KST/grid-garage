from base.geodata import describe_arc, table_conversion
from shutil import copyfile
import os
import csv


class ResultsUtils(object):
    def __init__(self):
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

    def initialise(self, params):
        self.result_table_output_parameter = params["result_table"]
        self.fail_table_output_parameter = params["fail_table"]

        self.output_workspace = params["output_workspace"]
        self.output_workspace_type = describe_arc(self.output_workspace).workspaceType

        self.output_workspace_parent = os.path.split(self.output_workspace)[0]

        if self.output_workspace_type == "RemoteDatabase":
            raise ValueError("Remote database workspaces are not yet supported")

        # if output is to a fgdb, put the csv into it's parent folder
        csv_ws = self.output_workspace_parent if self.output_workspace_type == "LocalDatabase" else self.output_workspace

        tn = params["result_table_name"]
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
            ret.append("Existing results csv at {0} removed".format(self.result_csv))
        except:
            pass
        try:
            os.remove(self.fail_csv)
            ret.append("Existing fail csv at {0} removed".format(self.fail_csv))
        except:
            pass

        if self.output_workspace_type == "LocalDatabase":
            ret.append("Temporary Results initialised:\nTemp Result CSV @ {0}\nTemp Failure CSV @ {1}".format(self.result_csv, self).fail_csv)
        else:
            ret.append("Results initialised:\nResult CSV @ {0}\nFailure CSV @ {1}".format(self.result_csv, self.fail_csv))

        return "\n".join(ret)

    def add(self, result):
        # writes a result to the temp CSV immediately, trade off between
        # runtime performance, RAM usage and FAILURE (i.e. recovery of results)
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
            setattr(self, "result_fieldnames", result[0].keys() if is_tuple else result.keys())
            with open(self.result_csv, "wb") as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', fieldnames=self.result_fieldnames)
                writer.writeheader()

        # write the data
        with open(self.result_csv, "ab") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.result_fieldnames)
            if is_tuple:
                writer.writerows(result)
                self.result_count += len(result)
            else:
                writer.writerow(result)
                self.result_count += 1

        return "Result written: {0}".format(result)

    def fail(self, geodata, e, row):
        # writes a fail to the temp CSV immediately, trade off between
        # runtime performance, RAM usage and failure (recovery of results)
        if not self.fail_csv:
            raise ValueError("Fail CSV is not set")

        err = str(e).strip().replace('\n', '|').replace('\r', '')

        # write the header on first call
        if not os.path.isfile(self.fail_csv):
            setattr(self, "failure_fieldnames", ["geodata", "failure", "row_data"])
            with open(self.fail_csv, "wb") as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', fieldnames=self.failure_fieldnames)
                writer.writeheader()

        # write the failure record
        with open(self.fail_csv, "ab") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.failure_fieldnames)
            writer.writerow({"geodata": geodata, "failure": err, "row_data": str(row)})
            self.fail_count += 1

    def write(self):
        return [self._write_results(), self._write_failures()]

    def _write_results(self):
        if not os.path.exists(self.result_csv):
            return "No results"

        err_msg = ""
        if self.output_workspace_type == "LocalDatabase":  # it's an fgdb
            try:
                self.result_table = table_conversion(self.result_csv, self.output_workspace, self.result_table_name)
                os.remove(self.result_csv)
            except:
                self.result_table = os.path.join(self.output_workspace_parent, self.result_table_name + ".csv")
                copyfile(self.result_csv, self.result_table)
                os.remove(self.result_csv)
                err_msg = "Table to Table Conversion failed. Hoisted temporary result CSV to database parent directory...\n"
        else:  # it's a directory
            self.result_table = self.result_csv

        self.result_table_output_parameter.value = self.result_table
        return err_msg + "Final results at {0}".format(self.result_table)

    def _write_failures(self):
        if not os.path.exists(self.fail_csv):
            return "No failures"

        err_msg = ""
        if self.output_workspace_type != "FileSystem":  # it's a a fgdb or rmdb
            try:
                self.fail_table = table_conversion(self.fail_csv, self.output_workspace, self.fail_table_name)
                os.remove(self.fail_csv)
            except:
                self.fail_table = os.path.join(self.output_workspace_parent, self.fail_table_name + ".csv")
                copyfile(self.fail_csv, self.fail_table)
                os.remove(self.fail_csv)
                err_msg = "Table to Table Conversion failed. Hoised temporary failure CSV to database parent directory...\n"
        else:
            self.fail_table = self.fail_csv

        self.fail_table_output_parameter.value = self.fail_table
        return err_msg + "Failures at {0}".format(self.fail_table)

# this message based status thing above is pretty dodgy needs to be reworked sensibly
