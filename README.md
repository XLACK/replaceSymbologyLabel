# -替换符号系统标注
使用arcpy实现替换符号系统标注，方法是通过Layer对象的_arc_object.renderer来实现替换标注，思路是gis.stackexchange.com中isamson的回答启发了我，原文地址为https://gis.stackexchange.com/questions/259673/how-to-change-or-assign-arcmap-layer-symbology-type-from-python，非常感谢这位大神的思路启发！！！
# 介绍
提供了自定义工具箱形式和python工具箱两种，两种工具箱使用方法相同，开发环境为ArcGIS10.2.2自带的python27，工具不依赖ArcGIS自带python库外的额外的第三方库，未在其他更高版本ArcGIS环境测试。
