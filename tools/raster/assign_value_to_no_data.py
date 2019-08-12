from base.base_tool import BaseTool
from base import utils
from base.decorators import input_tableview, input_output_table, parameter, raster_formats
import arcpy


tool_settings = {"label": "Assign Value to NoData",
                 "description": "Assgn a value to NoData...",
                 "can_run_background": "True",
                 "category": "Raster"}


class AssignValueToNodataRasterTool(BaseTool):
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
    @parameter("ndv_value", "Value for NoData Cells", "GPDouble", "Required", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table(affixing=True)
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

        ras = data['raster']

        utils.validate_geodata(ras, raster=True)

        r_out = utils.make_table_name(ras, self.output_file_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        ras = arcpy.Raster(ras)
        ndv = ras.noDataValue
        pix_type = ras.pixelType

        self.info("Nodata value is {}".format(ndv))

        if any(x in pix_type for x in ["S", "U"]):
            self.info("Raster pixel type is '{}' (integer)".format(pix_type))
            try:
                self.ndv_value = int(self.ndv_value)
                self.info("Nodata value cast to integer {}".format(self.ndv_value))
            except:
                self.info("New value for NDV cells '{0}' could not be coerced to integer, output raster will be floating point".format(self.ndv_value))
                pass

        self.info("Setting NDV cells on {1} to {0} -> {2}".format(self.ndv_value, ras, r_out))

        null_ras = arcpy.sa.IsNull(ras)

        out_ras = arcpy.sa.Con(null_ras, self.ndv_value, ras, "#")

        out_ras.save(r_out)

        return {"raster": r_out, "source_geodata": ras}
