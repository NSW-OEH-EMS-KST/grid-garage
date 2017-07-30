from base.base_tool import BaseTool
from base.results import result
import os
from base.method_decorators import input_tableview, input_output_table
import xml.etree.cElementTree as et

tool_settings = {"label": "Get IAR ID From XML",
                 "description": "Retrieves Internal Asset Register ID from XML",
                 "can_run_background": "False",
                 "category": "Metadata"}


@result
class GetIARIDFromXmlTool(BaseTool):
    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

    @input_tableview("xml_table", "Table for XML Files", False, ["xml:geodata:"])
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_parameter(self.get_ids, "xml_table", ["xml"])

        return

    def get_ids(self, data):

        xmlfile = data["xml"]

        if not os.path.exists(xmlfile):
            raise ValueError("XML file '{}' does not exist".format(xmlfile))

        self.info("Parsing {0}".format(xmlfile))

        tree = et.parse(xmlfile)
        root = tree.getroot()

        # 1.	FileID: /gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString
        file_id = root.find('{http://www.isotc211.org/2005/gmd}fileIdentifier').find('{http://www.isotc211.org/2005/gco}CharacterString').text

        # 2.	Title: /gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString
        title = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo').find('{http://www.isotc211.org/2005/gmd}MD_DataIdentification').find('{http://www.isotc211.org/2005/gmd}citation').find('{http://www.isotc211.org/2005/gmd}CI_Citation').find('{http://www.isotc211.org/2005/gmd}title').find('{http://www.isotc211.org/2005/gco}CharacterString').text

        # 3.	Dataset location: /gmd:MD_Metadata/gmd:dataSetURI
        ds_uri = root.find('{http://www.isotc211.org/2005/gmd}dataSetURI').find('{http://www.isotc211.org/2005/gco}CharacterString').text

        # https://iar.environment.nsw.gov.au/dataset/1BBFF75D-20EB-49F2-8653-FD6E688DDD3C/html
        # https://iar.environment.nsw.gov.au/dataset/7B00ED2AC4-F887-4655-86BA-CD9B24AB4E797D/html
        html_link = "https://iar.environment.nsw.gov.au/dataset/{0}/html".format(file_id[1:-1])

        return {"xml": xmlfile, "file_id": file_id, "title": title, "dataset_uri": ds_uri, "html_link": html_link}

