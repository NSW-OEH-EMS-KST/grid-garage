from base.base_tool import BaseTool
from base.class_decorators import results
from base.method_decorators import input_output_table, input_tableview
from datetime import datetime
from arcpy import Delete_management

note = \
""" Note (source ESRI):
    -Data currently in use in another ArcGIS application cannot be deleted: the tool fails with ERROR 000464.
    -Deleting a shapefile also deletes ancillary files such as the metadata, projection, and index files.
    -Deleting a folder moves the folder to the system Recycle Bin, where it can be restored or permanently deleted.
    -Deleting a geometric network demotes all the feature classes in the network to simple feature types; Edge feature classes become line feature classes; and junction feature classes become point feature classes. Deleting the network also deletes all the related network tables and the orphan junction feature class from the geodatabase.
    -Deleting a database connection file does not delete the ArcSDE database. A database connection file is simply a shortcut to the database.
    -Deleting a relationship class deletes the row corresponding to that relationship from the relationship table
 """

tool_settings = {"label": "Delete",
                 "description": "Deletes geodata...\n" + note,
                 "can_run_background": "True",
                 "category": "Geodata"}


@results
class DeleteGeodataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.start_iteration]

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def start_iteration(self):
        self.iterate_function_on_tableview(self.process, "geodata_table", ["geodata"])
        return

    def process(self, data):
        self.log.debug("IN data= {}".format(data))

        gd = data["geodata"]
        self.log.info('Deleting {0}'.format(gd))
        Delete_management(gd)

        r = self.results.add({'deleted_geodata': gd, 'time-deleted': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]})
        self.log.info(r)

        self.log.debug("OUT")
        return

