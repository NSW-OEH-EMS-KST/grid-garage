# geodata tools
from tools.feature.clip import ClipFeatureTool
from tools.feature.copy import CopyFeatureTool
from tools.feature.feature_to_raster import FeatureToRasterTool
from tools.feature.polygon_to_raster import PolygonToRasterTool
# feature tools
from tools.geodata.compare_extents import CompareExtentsGeodataTool
from tools.geodata.copy import CopyGeodataTool
from tools.geodata.delete import DeleteGeodataTool
from tools.geodata.describe import DescribeGeodataTool
from tools.geodata.display import DisplayGeodataTool
from tools.geodata.generate_names import GenerateNamesGeodataTool
from tools.geodata.list_workspace_tables import ListWorkspaceTablesGeodataTool
from tools.geodata.rename import RenameGeodataTool
from tools.geodata.search import SearchGeodataTool
from tools.geodata.select import SelectGeodataTool
# metadata tools
from tools.metadata.create_tips import CreateTipsTableMetadataTool
from tools.metadata.export_tips import ExportTipsToFileMetadataTool
from tools.metadata.export_xml import ExportXmlMetadataTool
from tools.metadata.import_tips import ImportTipFilesToTableMetadataTool
# raster tools
from tools.raster.aggregate import AggregateRasterTool
from tools.raster.block_statistics import BlockStatisticsRasterTool
from tools.raster.build_attribute_table import BuildAttributeTableRasterTool
from tools.raster.calculate_statistics import CalculateStatisticsRasterTool
from tools.raster.clip import ClipRasterTool
from tools.raster.copy import CopyRasterTool
from tools.raster.reclass_by_threshold import ReclassByThresholdRasterTool
from tools.raster.extract_values_to_points import ExtractValuesToPointsRasterTool
from tools.raster.lookup_by_table import LookupByTableRasterTool
from tools.raster.slice import SliceRasterTool
from tools.raster.zonal_stats_as_table import ZonalStatisticsAsTableTool
from tools.raster.properties import BandPropertiesRasterTool
from tools.raster.reclass_by_table import ReclassByTableRasterTool
from tools.raster.reproject import ReprojectRasterTool
from tools.raster.resample import ResampleRasterTool
from tools.raster.set_no_data_value import SetNodataValueRasterTool
from tools.raster.set_value_to_null import SetValueToNullRasterTool
from tools.raster.to_ascii import ToAsciiRasterTool
from tools.raster.transform import TransformRasterTool
from tools.raster.tweak_values import TweakValuesRasterTool
from tools.raster.values_at_points import ValuesAtPointsRasterTool
# cdf tools
from tools.cdf.describe_cdf import DescribeCdfTool
# from tools.cdf.to_standard_grid import ToStandardGridCdfTool
from tools.cdf.extract_timeslices import ExtractTimeslicesCdfTool
# from tools.cdf.export_cdf import ExportCdfTool
from tools.cdf.search_cdf import SearchCdfTool


class Toolbox(object):
    """
    """

    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Grid Garage"
        self.alias = "GridGarage"

        geodata_tools = {SearchGeodataTool,
                         CopyGeodataTool,
                         DescribeGeodataTool,
                         SelectGeodataTool,
                         DisplayGeodataTool,
                         CompareExtentsGeodataTool,
                         DeleteGeodataTool,
                         GenerateNamesGeodataTool,
                         RenameGeodataTool,
                         ListWorkspaceTablesGeodataTool}

        feature_tools = {FeatureToRasterTool,
                         PolygonToRasterTool,
                         CopyFeatureTool,
                         ClipFeatureTool}

        raster_tools = {AggregateRasterTool,
                        BandPropertiesRasterTool,
                        BlockStatisticsRasterTool,
                        BuildAttributeTableRasterTool,
                        CalculateStatisticsRasterTool,
                        ClipRasterTool,
                        CopyRasterTool,
                        LookupByTableRasterTool,
                        ReprojectRasterTool,
                        ReclassByTableRasterTool,
                        ReclassByThresholdRasterTool,
                        ResampleRasterTool,
                        SetNodataValueRasterTool,
                        SetValueToNullRasterTool,
                        SliceRasterTool,
                        ToAsciiRasterTool,
                        TransformRasterTool,
                        TweakValuesRasterTool,
                        ExtractValuesToPointsRasterTool,
                        ValuesAtPointsRasterTool,
                        ZonalStatisticsAsTableTool
                        }

        metadata_tools = {
                          CreateTipsTableMetadataTool,
                          ImportTipFilesToTableMetadataTool,
                          ExportTipsToFileMetadataTool,
                          ExportXmlMetadataTool,
                          }

        cdf_tools = {
                     SearchCdfTool,
                     DescribeCdfTool,
                     # ToStandardGridCdfTool,
                     ExtractTimeslicesCdfTool,
                     # ExportCdfTool
                     }

        self.tools = list(geodata_tools | feature_tools | raster_tools | metadata_tools | cdf_tools)


def test_tools():
    """

    """

    tb = Toolbox()
    for t in tb.tools:
        try:
            tool = t()
            print "Load test - {}".format(tool.label)
            tool.execute(tool.getParameterInfo(), None)
        except Exception as e:
            print e


if __name__ == "__main__":
    test_tools()
