# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import arcpy
import xml.etree.ElementTree as ET
import re

if __name__ == "__main__":
    layer = arcpy.GetParameter(0)
    labelMapping = arcpy.GetParameter(3)
    outputLyrPath = arcpy.GetParameterAsText(5)
    
    layerRenderer = layer._arc_object.renderer
    stdAttribMatch = re.search(r'<[^/!][^>]*>', layerRenderer).group()
    xmlRoot = ET.fromstring(layerRenderer)
    labelMappingDict = {labelMapping.getValue(_, 0): labelMapping.getValue(_, 1) for _ in range(labelMapping.rowCount)}
    
    valueInfo = xmlRoot.find("UniqueValueInfos").findall("UniqueValueInfo")
    
    for valueItem in valueInfo:
        value = valueItem.find("Value").text
        valueItem.find("Label").text = labelMappingDict[value]
    
    newLayerRenderer = ET.tostring(xmlRoot)
    wrongAttribMatch = re.search(r'<[^/!][^>]*>', newLayerRenderer).group()
    newLayerRenderer = newLayerRenderer.replace(wrongAttribMatch, stdAttribMatch)
    layer._arc_object.renderer = newLayerRenderer
    layer.saveACopy(outputLyrPath)
    arcpy.RefreshActiveView()
    
    







