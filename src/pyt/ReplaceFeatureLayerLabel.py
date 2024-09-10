import arcpy
import numpy as np
import xml.etree.ElementTree as ET
import re

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "toolBox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [ReplaceFeatureLayerLabel]


class ReplaceFeatureLayerLabel(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = u"替换要素图层符号标注"
        self.description = ""
        self.canRunInBackground = False
        self.desc = None
        self.xml =  None

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = u"图层",
            name = "Input Layer",
            datatype = "GPLayer",
            parameterType = "Required",
            direction = "Input")
        param1 = arcpy.Parameter(
            displayName = u"匹配字段",
            name = "Input FieldNmaeOfString",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input",
            enabled = False)
        param2 = arcpy.Parameter(
            displayName = u"映射字段",
            name = "Input Field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input")
        param3 = arcpy.Parameter(
            displayName = u"匹配关系",
            name = "Input ValueTable",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input")
        param4 = arcpy.Parameter(
            displayName = u"是否按匹配字段进行替换",
            name = "Input Bool",
            datatype = "GPBoolean",
            parameterType = "Optional",
            direction = "Input")
        param5 = arcpy.Parameter(
            displayName = u"输出图层文件路径",
            name = "Output LayerPath",
            datatype = "DELayer",
            parameterType = "Required",
            direction = "Output")
        param2.filter.list = ["SmallInteger", "Integer", "String", "Date", \
            "SHORT", "LONG", "TEXT", "DATE"]
        param2.parameterDependencies = [param0.name]
        param3.columns = [
            ['GPString', u'唯一值字段值'],
            ['GPString', u'替换字段值'],
            ['GPString', u'警告信息']]
        params = [param0, param1, param2, param3, param4, param5]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[4].value:
            parameters[1].parameterType = "Required"
            parameters[1].enabled = True
        else:
            parameters[1].parameterType = "Optional"
            parameters[1].enabled = False
        if parameters[0].value:
            lyrRenderer = parameters[0].value.renderer
            if lyrRenderer is not None:
                self.xml = ET.fromstring(lyrRenderer)
                Field1 = None if self.xml.find("Field1") is None else self.xml.find("Field1").text
                Field2 = None if self.xml.find("Field2") is None else self.xml.find("Field2").text
                Field3 = None if self.xml.find("Field3") is None else self.xml.find("Field3").text
                parameters[1].filter.list = list(filter(None, [Field1,Field2,Field3]))
            else:
                parameters[1].filter.list = None
        self.updateMessages(parameters)
        if parameters[0].value and parameters[2].value and not parameters[0].hasError() and not parameters[2].hasError() \
        and (not parameters[1].enabled or (parameters[1].value and not parameters[1].hasError())):
            fieldList = parameters[1].filter.list if not parameters[1].enabled else [parameters[1].value]
            UVI = self.xml.find("UniqueValueInfos").findall("UniqueValueInfo")
            FD = self.xml.find("FieldDelimiter").text
            valueTable = []
            arrayOfLayer = arcpy.da.TableToNumPyArray(parameters[0].value, fieldList + [str(parameters[2].value)])
            for value in UVI:
                values = list(value.find("Value").text.split(FD)) if not parameters[1].enabled else [value.find("Value").text]
                conditions = np.ones(len(arrayOfLayer), dtype = bool)
                for i, j in zip(fieldList, values):
                    conditions &= (arrayOfLayer[i] == j)
                filterArray = arrayOfLayer[str(parameters[2].value)][conditions]
                labelValueList = []
                for item in filterArray:
                    strItem = str(item)
                    if strItem.strip() and strItem not in labelValueList:
                        labelValueList.append(strItem)
                        if len(labelValueList) > 1:
                            break
                warning = u"无对应值或对应值不唯一" if len(labelValueList) != 1 else None
                valueTable.append([value.find("Value").text, labelValueList[0] if len(labelValueList) != 0 else "", warning])
            parameters[3].values = valueTable
        else:
            parameters[3].values = None
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        if parameters[0].value:
            if not arcpy.Exists(parameters[0].value.dataSource):
                parameters[0].setErrorMessage(u"图层数据源不存在。")
                return
            desc = arcpy.Describe(parameters[0].value)
            if desc.datatype != "FeatureLayer":
                parameters[0].setErrorMessage(u"图层类型错误，仅支持要素图层。")
                return
            else:
                self.desc = desc
            if not parameters[1].filter.list:
                parameters[0].setErrorMessage(u"所选图层无唯一值字段。")
                return
            if self.desc.FIDSet:
                parameters[0].setErrorMessage(u"所选图层存在被选择要素，请清空选择。")
                return
            if len(parameters[1].filter.list) != 1:
                parameters[0].setWarningMessage(u"所选图层非唯一值字段图层。")
        if parameters[0].value and parameters[1].enabled and not parameters[1].value:
            parameters[1].setErrorMessage(u"请选择匹配字段。")
            return
        if parameters[0].value and parameters[1].enabled and parameters[1].value:
            if self.desc.fieldInfo.findFieldByName(parameters[1].value) == -1:
                parameters[1].setErrorMessage(u"图层不包含此字段。")
                return
            elif self.desc.fields[self.desc.fieldinfo.findFieldByName(parameters[1].value)].type.lower() not in ['string', 'date']:
                parameters[1].setErrorMessage(u"所选字段必须为字符型字段。")
                return
            elif parameters[1].value != parameters[1].filter.list[0]:
                parameters[1].setWarningMessage(u"此字段非符号系统唯一值首选【值字段】。") 
        if parameters[0].value and parameters[2].value and self.desc.fieldInfo.findFieldByName(parameters[2].value) == -1:
            parameters[2].setErrorMessage(u"图层不包含此字段。")
            return
        if parameters[0].value and parameters[1].enabled and parameters[1].value and parameters[2].value:
            if parameters[1].value == str(parameters[2].value):
                parameters[2].setWarningMessage(u"所选字段与匹配字段重复。")
        if parameters[0].value and not parameters[1].enabled and parameters[2].value:
            if len(parameters[1].filter.list) == 1 and parameters[1].filter.list[0] == str(parameters[2].value):
                parameters[2].setWarningMessage(u"所选字段与默认匹配字段重复。")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        layer = parameters[0].value
        labelMapping = parameters[3].value
        outputLyrPath = str(parameters[5].value)
        
        layerRenderer = layer.renderer
        stdAttribMatch = re.search(r'<[^/!][^>]*>', layerRenderer).group()
        xmlRoot = ET.fromstring(layerRenderer)
        labelMappingDict = {_[0]: _[1] for _ in labelMapping}
    
        valueInfo = xmlRoot.find("UniqueValueInfos").findall("UniqueValueInfo")
    
        for valueItem in valueInfo:
            value = valueItem.find("Value").text
            valueItem.find("Label").text = labelMappingDict[value]
    
        newLayerRenderer = ET.tostring(xmlRoot)
        wrongAttribMatch = re.search(r'<[^/!][^>]*>', newLayerRenderer).group()
        newLayerRenderer = newLayerRenderer.replace(wrongAttribMatch, stdAttribMatch)
        layer.renderer = newLayerRenderer
        layer.save(outputLyrPath)
        arcpy.RefreshActiveView()
        return
