from base.base_tool import BaseTool
from base.results import result
from base import utils
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter, transform_methods, raster_formats
import arcpy

tool_settings = {"label": "Transform",
                 "description": "Transforms rasters...",
                 "can_run_background": "True",
                 "category": "Raster"}


@result
class TransformRasterTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("method", "Method", "GPString", "Required", False, "Input", transform_methods, None, None, transform_methods[0])
    @parameter("max_stretch", "Stretch to maximum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("min_stretch", "Stretch to minimum value", "GPDouble", "Optional", False, "Input", None, None, None, None, "Options")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def updateParameters(self, parameters):

        ps = [(i, p.name) for i, p in enumerate(parameters)]
        self.debug("TransformRasterTool.updateParameters {}".format(ps))

        p2, p3, p4 = parameters[2], parameters[3], parameters[4]

        stretch = p2.value == 'STRETCH'

        p3.enabled = p4.enabled = stretch

        if stretch and p3.valueAsText in [None, "", "#"]:
            p3.setIDMessage("ERROR", 735, p3.displayName)

        if stretch and p4.valueAsText in [None, "", "#"]:
            p4.setIDMessage("ERROR", 735, p4.displayName)

        BaseTool.updateParameters(self, parameters)

        return

    def updateMessages(self, parameters):

        # print [(i, p.name) for i, p in enumerate(parameters)]
        #
        # # BaseTool.updateMessages(self, parameters)
        # stretch = parameters[2].value == 'STRETCH'
        # if stretch and not parameters[6].valueAsText:
        #     parameters[6].setIDMessage("ERROR", 735, parameters[3].displayName)
        # if stretch and not parameters[7].valueAsText:
        #     parameters[7].setIDMessage("ERROR", 735, parameters[4].displayName)

        return

    def iterate(self):

        self.iterate_function_on_tableview(self.transform, "raster_table", ["geodata"], return_to_results=True)

        return

    def get_property(self, raster, property):

        v = arcpy.GetRasterProperties_management(raster, property)
        v = v.getOutput(0)
        self.debug("for raster {} property {} has type {} ".format(raster, property, type(v)))

        return float(v)

    def transform(self, data):

        r_in = data["geodata"]
        utils.validate_geodata(r_in, raster=True)

        r_out = utils.make_raster_name(r_in, self.result.output_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)

        self.info("\tCalculating statistics")
        arcpy.CalculateStatistics_management(r_in)

        raster_mean = self.get_property(r_in, "MEAN")
        raster_std = self.get_property(r_in, "STD")
        raster_min = self.get_property(r_in, "MINIMUM")
        raster_max = self.get_property(r_in, "MAXIMUM")
        self.info("\tStatistics Mean/Std/Min/Max: {}/{}/{}/{}".format(raster_mean, raster_std, raster_min, raster_max))

        self.info("Transforming raster {} using method {}".format(r_in, self.method))
        ras = arcpy.Raster(r_in)

        if self.method == "STANDARDISE":
            ras = (ras - raster_mean) / raster_std

        elif self.method == "STRETCH":  # (INVAL - INLO) * ((OUTUP-OUTLO)/(INUP-INLO)) + OUTLO
            if raster_min == raster_max:
                raise ValueError("Minimum value = Maximum value, stretching is not applicable")
            else:
                scale = (self.max_stretch - self.min_stretch) / (raster_max - raster_min)
                ras = (ras - raster_min) * scale + self.min_stretch

        elif self.method == "NORMALISE":
            if raster_min == raster_max:
                raise ValueError("Minimum value = Maximum value, normalising is not applicable")
            else:
                ras = (ras - raster_min) / (raster_max - raster_min)

        elif self.method == "LOG":
            ras = arcpy.sa.Ln(r_in)

        elif self.method == "SQUAREROOT":
            ras = arcpy.sa.SquareRoot(r_in)

        elif self.method == "INVERT":
            ras = (ras - (raster_max - raster_min)) * -1

        # save and exit
        self.info('\tSaving to {0}'.format(r_out))
        ras.save(r_out)

        data["method"] = self.method

        return {"geodata": r_out, "source_geodata": r_in, "transform": data}

        # this numpy stuff.. numpyarraytoraster just not behaving
        # self.send_info(data)
        # r_in = data["raster"]
        # if not self.geodata.exists(r_in):
        #     raise DoesNotExistError(r_in)
        #
        # _, __, ras_name, ras_ext = split_up_filename(r_in)
        # r_out = self.geodata.make_raster_name(r_in, self.results.output_workspace, self.raster_format)
        # self.send_info("Transforming raster {0} -->> {1} using method {2}".format(r_in, r_out, self.method))
        #
        # # get some properties
        # np_type_map = {"U1": "uint8", "U2": "uint8", "U4": "uint8", "U8": "uint8", "S8": "int8", "U16": "uint16", "S16": "int16", "U32": "uint32", "S32": "int32", "F32": "float32", "F64": "float64"}
        # rast = ap.Raster(r_in)
        # np_type = np_type_map[rast.pixelType]
        # xmin_in, ymin_in = rast.extent.XMin, rast.extent.YMin
        # xwidth_in, ywidth_in = rast.meanCellWidth, rast.meanCellHeight
        # ndv_in = rast.noDataValue
        # del rast
        #
        # self.send_info("...reading raster array...")
        # array_in = ap.RasterToNumPyArray(r_in)
        # array_in = np.array(array_in, dtype=np_type)
        # self.send_info(array_in)
        #
        # self.send_info("...masking array with '{}'...".format(ndv_in))
        # mask = np.where(array_in == ndv_in, True, False)
        # array_masked = np.ma.array(array_in, mask=mask)
        # self.send_info(array_masked)
        #
        # mean, stdv, minv, maxv = array_masked.mean(), array_masked.std(), array_masked.min(), array_masked.max()
        # self.send_info('mean={} stdv={} max={} min={}'.format(mean, stdv, maxv, minv))
        #
        # array_out = array_masked
        # if self.method == "STANDARDISE":
        #     array_out = (array_masked - mean) / stdv
        #
        # elif self.method == "STRETCH":  # (INVAL - INLO) * ((OUTUP-OUTLO)/(INUP-INLO)) + OUTLO
        #     if minv == maxv:
        #         raise ValueError("Minimum value = Maximum value, normalising is not applicable")
        #     else:
        #         scale = (self.max_stretch - self.min_stretch) / (maxv - minv)
        #         array_out = (array_masked - minv) * scale + self.min_stretch
        #
        # elif self.method == "NORMALISE":
        #     if minv == maxv:
        #         raise ValueError("Minimum value = Maximum value, normalising is not applicable")
        #     else:
        #         array_out = (array_masked - minv) / (maxv - minv)
        #
        # elif self.method == "LOG":
        #     array_out = array_masked.log()
        #
        # elif self.method == "SQUAREROOT":
        #     array_out = array_masked.sqrt()
        #
        # elif self.method == "INVERT":
        #     array_out = (array_masked - (maxv + minv)) * -1
        #
        # minv_qc, maxv_qc = array_out.min(), array_out.max()
        # self.send_info('{}, {}) --> ({}, {})\n{}'.format(minv, maxv, minv_qc, maxv_qc, array_out))
        #
        # self.send_info("...casting to original data type...")
        # array_out = array_out.data.astype(np_type)
        # minv_qc, maxv_qc = array_out.min(), array_out.max()
        # self.send_info('{}, {}) --> ({}, {})\n{}'.format(minv, maxv, minv_qc, maxv_qc, array_out))
        #
        # self.send_info("...saving to '{}'...".format(r_out))
        # ap.env.overwriteOutput = True
        # ap.env.outputCoordinateSystem = r_in
        # ap.env.cellSize = r_in
        # ap.env.Extent = r_in
        # ap.env.snapRaster = r_in
        # ras_out = ap.NumPyArrayToRaster(array_out, ap.Point(xmin_in, ymin_in), xwidth_in, ywidth_in, ndv_in)
        # ras_out.save(r_out)
        # data["method"] = self.method
        # self.result.add({"geodata": r_out, "source_geodata": r_in, "transform": data})

        # return



    # def set_nodata():
#     import os
#     # import Snippets
#     from base.comtypes import client
#     from base.comtypes.gen import esriGeoDatabase as esriGeoDatabase
#     from base.comtypes.gen import esriDataSourcesRaster as esriDataSourcesRaster
#
#     # Absolute path to the raster
#     raster = r'C:\Temp\myMultiBandRaster.tif'
#
#     # NoData values list for each of the 3 bands
#     noDataValuesList = [15, 0, 34]
#
#     # Open the workspace
#     pWSFactory = snippets.NewObj(esriDataSourcesRaster.RasterWorkspaceFactory, esriGeoDatabase.IWorkspaceFactory2)
#     pWS = pWSFactory.OpenFromFile(os.path.dirname(raster), 0)
#
#     # Open the raster dataset
#     pRasterWS = pWS.QueryInterface(esriDataSourcesRaster.IRasterWorkspace)  # Cast to 'IRasterWorkspace' to call 'OpenRasterDataset' function
#     pRasterDataset = pRasterWS.OpenRasterDataset(os.path.basename(raster))
#
#     # Get access to bands
#     pRasterBands = pRasterDataset.QueryInterface(esriDataSourcesRaster.IRasterBandCollection)
#
#     for index, val in enumerate(noDataValuesList):
#         # Get band
#         pBand = pRasterBands.Item(index)
#         # Get corresponding properties object
#         pPropsBand = pBand.QueryInterface(esriDataSourcesRaster.IRasterProps)
#         # Set noData value
#         pPropsBand.NoDataValue = val