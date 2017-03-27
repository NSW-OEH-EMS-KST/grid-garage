import base.base_tool
import base.results
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, raster_formats, pixel_type, raster_formats2, input_output_raster_format
import arcpy
import base.utils


tool_settings = {"label": "Copy",
                 "description": "Copy rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@base.results.result
class CopyRasterTool(base.base_tool.BaseTool):

    def __init__(self):

        base.base_tool.BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        # self.config_keyword = None
        # self.background_value = None
        # self.nodata_value = None
        # self.onebit_to_eightbit = None
        # self.colormap_to_RGB = None
        # self.pixel_type = None
        # self.scale_pixel_value = None
        # self.RGB_to_Colormap = None
        # self.format = None
        # self.transform = None

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @parameter("config_keyword", "Config Keyword", "GPString", "Optional", False, "Input", None, None, None, None)
    @parameter("background_value", "Background Value", "GPDouble", "Optional", False, "Input", None, None, None, None)
    @parameter("nodata_value", "NoData Value", "GPString", "Optional", False, "Input", None, None, None, None)
    @parameter("onebit_to_eightbit", "1 bit to 8 bit", "GPString", "Optional", False, "Input", ["NONE", "OneBitTo8Bit"], None, None, "NONE")
    @parameter("colormap_to_RGB", "Colourmap to RGB", "GPString", "Optional", False, "Input", ["NONE", "ColormapToRGB"], None, None, "NONE")
    @parameter("pixel_type", "Pixel Type", "GPString", "Optional", False, "Input", pixel_type, None, None, None)
    @parameter("scale_pixel_value", "Scale Pixel value", "GPString", "Optional", False, "Input", ["NONE", "ScalePixelValue"], None, None, None)
    @parameter("RGB_to_Colormap", "RGB to Colourmap", "GPString", "Optional", False, "Input", ["NONE", "RGBToColormap"], None, None, None)
    @parameter("format", "Output Raster Format", "GPString", "Optional", False, "Input", raster_formats2, None, None, None)
    @parameter("transform", "Transform", "GPString", "Optional", False, "Input", None, None, None, None)
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return base.base_tool.BaseTool.getParameterInfo(self)

    def initialise(self):
        # p = self.get_parameter_dict()
        # self.config_keyword = p["config_keyword"] if p["config_keyword"] else "#"
        # self.background_value = p["background_value"] if p["background_value"] else "#"
        # self.nodata_value = p["nodata_value"] if p["nodata_value"] else "#"
        # self.onebit_to_eightbit = p["onebit_to_eightbit"] if p["onebit_to_eightbit"] else "NONE"
        # self.colormap_to_RGB = p["colormap_to_RGB"] if p["colormap_to_RGB"] else "NONE"
        # self.pixel_type = p["pixel_type"] if p["pixel_type"] else "#"
        # self.scale_pixel_value = p["scale_pixel_value"] if p["scale_pixel_value"] else "NONE"
        # self.RGB_to_Colormap = p["RGB_to_Colormap"] if p["RGB_to_Colormap"] else "NONE"
        # self.format = p["format"] if p["format"] else ""
        # self.transform = p["transform"] if p["transform"] else "#"

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.copy, "raster_table", ["raster"])

        return

    def copy(self, data):

        self.log.info(data)
        ras = data["raster"]
        self.log.info(ras)
        base.utils.validate_geodata(ras, raster=True)
        # self.send_info("validate_geodata done")
        # self.send_info([ras, self.results.output_workspace, self.format])
        ras_out = base.utils.make_raster_name(ras, self.results.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
        self.send_info("Copying {0} -->> {1} ...".format(ras, ras_out))
        # CopyRaster_management (in_raster, out_rasterdataset, {config_keyword}, {background_value}, {nodata_value}, {onebit_to_eightbit}, {colormap_to_RGB}, {pixel_type}, {scale_pixel_value}, {RGB_to_Colormap}, {format}, {transform})
        arcpy.CopyRaster_management(ras, ras_out, self.config_keyword, self.background_value, self.nodata_value, self.onebit_to_eightbit, self.colormap_to_RGB, self.pixel_type, self.scale_pixel_value, self.RGB_to_Colormap, self.format, self.transform)

        self.result.add({"geodata": ras_out, "source_geodata": ras})

        return

"http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/copy-raster.htm"
