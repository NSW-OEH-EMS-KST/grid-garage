from base.base_tool import BaseTool

from base.utils import split_up_filename, validate_geodata
from base.decorators import input_tableview, input_output_table
import arcpy
from os.path import exists, join
from hermes import Paperwork
from datetime import datetime


tool_settings = {"label": "Audit",
                 "description": "Audit datasets for identifiable metadata",
                 "can_run_background": "False",
                 "category": "Metadata"}


class AuditMetadataTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("geodata_table", "Table of Geodata", False, ["geodata:geodata:"])
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.audit, "geodata_table", ["geodata"], return_to_results=True)

        return

    def audit(self, data):

        geodata = data["geodata"]

        validate_geodata(geodata, message_func=self.info)

        self.info("Auditing {0}".format(geodata))

        desc = arcpy.Describe(geodata)

        pw = Paperwork(dataset=geodata)

        meta = pw.convert()
        meta['metadata']['grid_garage'] = {}
        # meta['metadata']['grid_garage']['metadata_audit'] = {"@date": datetime.now().time(), }

        pw.save(meta)

        tip_file = tip = None
        xml_file = xml = None

        workspace_type = arcpy.Describe(desc.path).workspaceType

        if workspace_type == "FileSystem":
            gd_path,  gd_base, gd_name, gd_ext = split_up_filename(geodata)

            xml_file = join(gd_path, gd_base + ".xml")
            if exists(xml_file):
                with open(xml_file, "r") as xmlfile:
                    xml = "".join(line.rstrip() for line in xmlfile)
            else:
                xml_file = None

            # html_file = join(gd_path, gd_name + ".html")
            # if exists(html_file):
            #     with open(html_file, "r") as htmlfile:
            #         html = "".join(line.rstrip() for line in htmlfile)
            # else:
            #     html_file = "{0} does not exist".format(html_file)

            # pdf_file = join(gd_path, gd_name + ".pdf")
            # if exists(pdf_file):
            #     pass  # not now
            # else:
            #     pdf_file = "{0} does not exist".format(pdf_file)

            tip_file = join(gd_path, gd_name + ".tip")
            if exists(tip_file):
                pass
            else:
                tip_file = None
        #     # lines = [line.rstrip() for line in open(tip_file)]
        #     # lines = [l.replace(":", "=", 1) for l in lines]
        #     # # lines = ["title={0}".format(l) for l in lines if not ":"]
        #     # lined = {}
        #     # for line in lines:
        #     #     if ":" not in line:
        #     #         line = "title={0}".format(line)
        #     #     p = line.split("=")
        #     #     if len(p) == 1:
        #     #         p.insert(0, "title=")
        #     #     elif len(p) > 2:
        #     #         s = ""
        #     #         for i in range(1, len(p)):
        #     #             s += p[i]
        #     #         p[1] = s
        #     #     lined[p[0]] = p[1]
        #     # tip = str(lined)
        #     with open(tip_file, "r") as tipfile:
        #         tips = [line.rstrip() for line in tipfile]
        #     if tips:
        #         tips = [t for t in tips if t]
        #         tipd = OrderedDict()
        #         tipd["title"] = tips[0]
        #         for t in tips[1:]:
        #             a, b = t.split(":", 1)
        #             tipd[a] = b
        #         tip = "{0}".format(tipd)
        # else:
        #     tip_file = None
            # with open(tip_file, "r") as tipfile:
            #     tip = "||".join(line.rstrip() for line in tipfile)
                # tiplines = tip.split("||")
                # title = tiplines[0]
                # tool.info(title)
                # tool.info(tiplines[1:])
                # tool.info([t.split(":") for t in tiplines[1:]])
                # try:
                #     tips = {k: v for k, v in [t.split(":") for t in tiplines[1:]]}
                # except:
                #     tips = "Error parsing tip file"

        #     else:
        #         tip_file = "{0} does not exist".format(tip_file)
        #
        # self.result.add({"geodata": geodata, "metadataRetrieved": metadataRetrieved,
        #                  "tip_file": tip_file, "tip": tip, "xml_file": xml_file, "xml": xml,
        #                  "html_file": html_file, "html": html})  #, "pdf_file": pdf_file})

        return {"geodata": geodata,  # "metadataRetrieved": metadata_retrieved,
                "workspace_type": workspace_type,
                "meta": meta,
                "tip_file": tip_file, "tip": tip,
                "xml_file": xml_file, "xml": xml}  #,
                # "html_file": html_file, "htmldf}

#
# """
# This script looks through the specified geodatabase and reports the
# names of all data elements, their schema owners and their feature
# dataset (if applicable). Certain metadata elements such as abstract,
# purpose and search keys are also reported.
#
# The output is a CSV file that can be read by Excel, ArcGIS, etc.
#
# Only geodatabases are supported, not folder workspaces.
#
# Note: If run from outside of ArcToolbox, you will need to add
# the metadata tool assemblies to the Global Assembly Cache.
# See: http://forums.arcgis.com/threads/74468-Python-Errors-in-IDLE-when-processing-metadata
#
# Parameters:
#     0 - Input workspace (file geodatabase, personal geodatabase,
#             or SDE connection file)
#     1 - Output CSV file
#
# Date updated: 2/11/2013
# """

# if __name__ == '__main__':
#     workspace = arcpy.GetParameterAsText(0)
#     csvFile = arcpy.GetParameterAsText(1)
#     headerRow = CreateHeaderRow()
#     print headerRow
#     datasetRows = ListWorkspaceContentsAndMetadata(workspace)
#     WriteCSVFile(csvFile, datasetRows, headerRow)


