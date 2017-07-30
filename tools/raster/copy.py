from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats, pixel_type, raster_formats2
import arcpy


tool_settings = {"label": "Copy",
                 "description": "Copy rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class CopyRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("raster_format", "Output Raster Format", "GPString", "Optional", False, "Input", raster_formats2, None, None, "Esri Grid")
    @parameter("config_keyword", "Config Keyword", "GPString", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("background_value", "Background Value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("nodata_value", "NoData Value", "GPString", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("onebit_to_eightbit", "1 bit to 8 bit", "GPString", "Optional", False, "Input", ["NONE", "OneBitTo8Bit"], None, None, "NONE", "Options")
    @parameter("colormap_to_RGB", "Colourmap to RGB", "GPString", "Optional", False, "Input", ["NONE", "ColormapToRGB"], None, None, "NONE", "Options")
    @parameter("pixel_type", "Pixel Type", "GPString", "Optional", False, "Input", pixel_type, None, None, None, "Options")
    @parameter("scale_pixel_value", "Scale Pixel value", "GPString", "Optional", False, "Input", ["NONE", "ScalePixelValue"], None, None, None, "Options")
    @parameter("RGB_to_Colormap", "RGB to Colourmap", "GPString", "Optional", False, "Input", ["NONE", "RGBToColormap"], None, None, None, "Options")
    @parameter("transform", "Transform", "GPString", "Optional", False, "Input", None, None, None, None, "Options")
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.copy, "raster_table", ["geodata"], return_to_results=True)

        return

    def copy(self, data):

        ras = data["geodata"]

        utils.validate_geodata(ras, raster=True)
        ras_out = utils.make_raster_name(ras, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.info("Copying {0} -->> {1} ...".format(ras, ras_out))
        # arcpy.CopyRaster_management(ras, ras_out, self.config_keyword, self.background_value, self.nodata_value, self.onebit_to_eightbit, self.colormap_to_RGB, self.pixel_type, self.scale_pixel_value, self.RGB_to_Colormap, self.raster_format, self.transform)
        arcpy.CopyRaster_management(ras, ras_out, self.config_keyword, self.background_value, self.nodata_value, self.onebit_to_eightbit, self.colormap_to_RGB, self.pixel_type, self.scale_pixel_value, self.RGB_to_Colormap, None, self.transform)

        return {"geodata": ras_out, "source_geodata": ras}

# "http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy-raster.htm"
# CopyRaster_management (in_raster, out_rasterdataset, {config_keyword}, {background_value}, {nodata_value}, {onebit_to_eightbit}, {colormap_to_RGB}, {pixel_type}, {scale_pixel_value}, {RGB_to_Colormap}, {format}, {transform})
