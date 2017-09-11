from base.base_tool import BaseTool
from base.results import result
from base.utils import validate_geodata, split_up_filename, join_up_filename
from base.method_decorators import input_tableview, input_output_table, parameter
import arcpy
from os.path import join, exists
from hermes import Paperwork


tool_settings = {"label": "Export Metadata",
                 "description": "Exports data source metadata to xml/html",
                 "can_run_background": "False",
                 "category": "Metadata"}


install_dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
# default_translator = join(install_dir, "Metadata", "Translator", "ARCGIS2ISO19139.xml")  # ESRI_ISO2ISO19139.xml")
default_stylesheet = join(install_dir, "Metadata", "Stylesheets", "ArcGIS.xsl")  # ESRI_ISO2ISO19139.xml")


@result
class ExportXmlMetadataTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @parameter("xml_folder", "Output Folder", "DEFolder", "Required", False, "Input", None, None, None, None)
    # @parameter("translator", "Translator", "DEFile", "Required", False, "Input", None, None, None, default_translator, None)
    @parameter("stylesheet", "Style Sheet", "DEFile", "Required", False, "Input", None, None, None, default_stylesheet, None)
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        # if not exists(self.translator):
        #     raise ValueError("Translator '{}' does not exist".format(self.translator))

        if not exists(self.stylesheet):
            raise ValueError("Stylesheet '{}' does not exist".format(self.stylesheet))

        self.iterate_function_on_tableview(self.export, "geodata_table", ["geodata"], return_to_results=True)

        return

    def export(self, data):

        geodata = data["geodata"]

        validate_geodata(geodata, message_func=self.info)

        self.info("Exporting XML/HTML files for {}".format(geodata))

        fpath, fname, fbase, fext = split_up_filename(geodata)

        xml_file = join_up_filename(self.xml_folder, fname, ".xml")
        html_file = join_up_filename(self.xml_folder, fbase, ".html")

        self.info("Attempting metadata upgrade")
        try:
            arcpy.UpgradeMetadata_conversion(geodata, "ESRIISO_TO_ARCGIS")
        except Exception as e:
            self.warn("Upgrade ESRIISO_TO_ARCGIS failed: {}".format(e))
            try:
                arcpy.UpgradeMetadata_conversion(geodata, "FGDC_TO_ARCGIS")
            except Exception as e:
                self.warn("Upgrade FGDC_TO_ARCGIS failed: {}".format(e))

        self.info("Creating metadata xml")
        try:
            pw = Paperwork(dataset=geodata)
            md = pw.convert()
            # pw.save(d=md)
            pw.exportToXML(self.xml_folder, fbase)
            self.info("XML file '{}' created".format(xml_file))
        except Exception as e:
            xml_file = "Error creating '{}': {}".format(xml_file, e)
            self.warn(xml_file)

        self.info("Creating metadata html")
        try:
            arcpy.XSLTransform_conversion(xml_file, self.stylesheet, html_file, "#")
            self.info("HTML file '{}' created".format(html_file))
        except:
            try:
                arcpy.XSLTransform_conversion(geodata, self.stylesheet, html_file, "#")
                self.info("HTML file '{}' created".format(html_file))
            except Exception as e:
                html_file = "Error creating '{}': {}".format(html_file, e)
                self.warn(html_file)

        return {"geodata": geodata, "xml_file": xml_file, "html_file": html_file}

        #
        # workspace_type = arcpy.Describe(desc.path).workspaceType
        #
        # if workspace_type == "FileSystem":
        #     gd_path,  gd_base, gd_name, gd_ext = split_up_filename(geodata)
        #
        #     xml_file = join(gd_path, gd_base + ".xml")
        #     if exists(xml_file):
        #         with open(xml_file, "r") as xmlfile:
        #             xml = "".join(line.rstrip() for line in xmlfile)
        #     else:
        #         xml_file = None
        # # metadata = md.MetadataEditor(geodata)  # currently supports Shapefiles, FeatureClasses, RasterDatasets and Layers
        # # self.info(metadata.__dict__)
        # # metadata.finish()
        # try:
        #     arcpy.ExportMetadata_conversion(geodata, self.translator, xml_file)
        #     self.info("XML file '{}' created".format(xml_file))
        # except Exception as e:
        #     xml_file = "Error creating '{}': {}".format(xml_file, e)
        #
        # html_file = join_up_filename(self.xml_folder, fbase, ".html")
        #


# import arcpy
# from arcpy import env
# env.workspace = "C:/data"
# # set local variables
# dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
# translator = dir + "Metadata/Translator/ESRI_ISO2ISO19139.xml"
# arcpy.ExportMetadata_conversion("data.gdb/roads", translator,
#                                 "roads_19139.xml")

# import arcpy
# from arcpy import env
# env.workspace = "C:/data"
# #set local variables
# dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
# xslt = dir + "Metadata/Stylesheets/ArcGIS.xsl"
# arcpy.XSLTransform_conversion("vegetation", xslt, "vegetation.html", "#")

