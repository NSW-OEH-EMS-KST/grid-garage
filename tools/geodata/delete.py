from base.base_tool import BaseTool
from base.decorators import input_output_table, input_tableview
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


class DeleteGeodataTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview()
    @input_output_table()
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.delete, return_to_results=True)

        return

    def delete(self, data):
        """

        Args:
            data:

        Returns:

        """

        gd = data["geodata"]
        self.info('Deleting {0}'.format(gd))
        Delete_management(gd)

        return {'deleted_geodata': gd, 'time-deleted': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}

