import arcpy
import xml.etree.ElementTree as ET
class ToolValidator(object):
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    self.params = arcpy.GetParameterInfo()
    self.desc = None
    self.xml =  None

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    self.params[1].enabled = False
    self.params[2].parameterDependencies = [self.params[0].name]
    self.params[3].columns = [['GPString', u'唯一值字段值'], ['GPString', u'替换字段值'], ['GPString', u'警告信息']]
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parameter
    has been changed."""
    if self.params[4].value:
        self.params[1].parameterType = "Required"
        self.params[1].enabled = True
    else:
        self.params[1].parameterType = "Optional"
        self.params[1].enabled = False
    if self.params[0].value:
        lyrRenderer = self.params[0].value._arc_object.renderer
        if lyrRenderer is not None:
            self.xml = ET.fromstring(lyrRenderer)
            Field1 = None if self.xml.find("Field1") is None else self.xml.find("Field1").text
            Field2 = None if self.xml.find("Field2") is None else self.xml.find("Field2").text
            Field3 = None if self.xml.find("Field3") is None else self.xml.find("Field3").text
            self.params[1].filter.list = list(filter(None, [Field1,Field2,Field3]))
        else:
            self.params[1].filter.list = None
    self.updateMessages()
    if self.params[0].value and self.params[2].value and not self.params[0].hasError() and not self.params[2].hasError() \
    and (not self.params[1].enabled or (self.params[1].value and not self.params[1].hasError())):
        desc = arcpy.Describe(self.params[0].value)
        fieldList = self.params[1].filter.list if not self.params[1].enabled else [self.params[1].value]
        clauseField = [arcpy.AddFieldDelimiters(self.params[0].value.dataSource, _) for _ in fieldList]
        UVI = self.xml.find("UniqueValueInfos").findall("UniqueValueInfo")
        FD = self.xml.find("FieldDelimiter").text
        valueTable = []
        for value in UVI:
            clause = []
            values = list(value.find("Value").text.split(FD)) if not self.params[1].enabled else [value.find("Value").text]
            for i,j,k in zip(clauseField,fieldList, values):
                fieldType = desc.fields[desc.fieldinfo.findFieldByName(j)].type
                if fieldType == 'String':
                    clause.append(i + " = " + "'" + k + "'")
                elif fieldType == 'Date':
                    clause.append(i + " = " + "date '" + k + "'")
                else:
                    clause.append(i + " = " + k)
            labelValueList = []
            for row in arcpy.da.SearchCursor(self.params[0].value, str(self.params[2].value), ' and '.join(clause)):
                rowStr = str(row[0])
                if rowStr.strip() and rowStr not in labelValueList:
                    labelValueList.append(rowStr)
                    if len(labelValueList) > 1:
                        break
            warning = u"无对应值或对应值不唯一" if len(labelValueList) != 1 else None
            valueTable.append([value.find("Value").text, labelValueList[0] if len(labelValueList) != 0 else "", warning])
        self.params[3].values = valueTable
    else:
        self.params[3].values = None
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    if self.params[0].value:
        if not arcpy.Exists(self.params[0].value.dataSource):
            self.params[0].setErrorMessage(u"图层数据源不存在。")
            return
        desc = arcpy.Describe(self.params[0].value)
        if desc.datatype != "FeatureLayer":
            self.params[0].setErrorMessage(u"图层类型错误，仅支持要素图层。")
            return
        else:
            self.desc = desc
        if not self.params[1].filter.list:
            self.params[0].setErrorMessage(u"所选图层无唯一值字段。")
            return
        if self.desc.FIDSet:
            self.params[0].setErrorMessage(u"所选图层存在被选择要素，请清空选择。")
            return
        if len(self.params[1].filter.list) != 1:
            self.params[0].setWarningMessage(u"所选图层非唯一值字段图层。")
    if self.params[0].value and self.params[1].enabled and not self.params[1].value:
        self.params[1].setErrorMessage(u"请选择匹配字段。")
        return
    if self.params[0].value and self.params[1].enabled and self.params[1].value:
        if self.desc.fieldInfo.findFieldByName(self.params[1].value) == -1:
            self.params[1].setErrorMessage(u"图层不包含此字段。")
            return
        elif self.desc.fields[self.desc.fieldinfo.findFieldByName(self.params[1].value)].type not in ['String', 'Date']:
            self.params[1].setErrorMessage(u"所选字段必须为字符型字段。")
            return
        elif self.params[1].value != self.params[1].filter.list[0]:
            self.params[1].setWarningMessage(u"此字段非符号系统唯一值首选【值字段】。") 
    if self.params[0].value and self.params[2].value and self.desc.fieldInfo.findFieldByName(self.params[2].value) == -1:
        self.params[2].setErrorMessage(u"图层不包含此字段。")
        return
    if self.params[0].value and self.params[1].enabled and self.params[1].value and self.params[2].value:
        if self.params[1].value == str(self.params[2].value):
            self.params[2].setWarningMessage(u"所选字段与匹配字段重复。")
    if self.params[0].value and not self.params[1].enabled and self.params[2].value:
        if len(self.params[1].filter.list) == 1 and self.params[1].filter.list[0] == str(self.params[2].value):
            self.params[2].setWarningMessage(u"所选字段与默认匹配字段重复。")
    return