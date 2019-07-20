from base.base_tool import BaseTool
from base import utils
from base.decorators import input_tableview, input_output_table, parameter, raster_formats
import arcpy


tool_settings = {"label": "Set NoData Value",
                 "description": "Set NoData Value...",
                 "can_run_background": "True",
                 "category": "Raster"}


class SetNodataValueRasterTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="raster")
    @parameter("ndv", "NoData Value", "GPDouble", "Required", False, "Input", None, None, None, None)
    @input_output_table(affixing=False, out_file_workspace=False)
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.set_ndv, return_to_results=True)

        return

    def set_ndv(self, data):
        """

        Args:
            data:

        Returns:

        """

        in_ras = data['raster']

        utils.validate_geodata(in_ras, raster=True)

        # should we, in the future, make a copy of data rather than in-situ changes... an option...?
        # out_ras = utils.make_raster_name(in_ras, self.output_file_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        ndv = int(self.ndv)
        bands = [1]  # at another time this can be updated to accommodate multi-band data

        ndvs = [[str(b), ndv] for b in bands]

        r = arcpy.Raster(in_ras)
        self.info("NDV on {0} is {1}".format(in_ras, r.noDataValue))
        del r

        self.info("Setting NDV {0} on {1}".format(ndv, in_ras))
        arcpy.SetRasterProperties_management(in_raster=in_ras, nodata=ndvs)

        r = arcpy.Raster(in_ras)
        self.info("NDV is now {0}".format(r.noDataValue))
        del r

        return {"raster": in_ras, "source_geodata": in_ras}
