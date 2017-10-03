from base.base_tool import BaseTool

from base import utils
from base.decorators import input_tableview, input_output_table, parameter, resample_methods, raster_formats
import arcpy

tool_settings = {"label": "Resample",
                 "description": "Resample rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


class ResampleRasterTool(BaseTool):
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
    @parameter("resample_type", "Resampling Method", "GPString", "Required", False, "Input", resample_methods, "resamplingMethod", None, None)
    @parameter("cell_size", "Cell Size", "GPSACellSize", "Required", False, "Input", None, "cellSize", None, None)
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

        self.iterate_function_on_tableview(self.resample, return_to_results=True)

        return

    def resample(self, data):
        """

        Args:
            data:

        Returns:

        """

        ras = data["raster"]

        utils.validate_geodata(ras, raster=True)

        ras_out = utils.make_raster_name(ras, self.output_file_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.info("Resampling {0} -->> {1} ...".format(ras, ras_out))

        arcpy.Resample_management(ras, ras_out, self.cell_size, self.resample_type)

        return {"raster": ras_out, "source_geodata": ras}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/resample.htm"


