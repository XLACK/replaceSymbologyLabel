# 替换符号系统标注
使用arcpy实现替换符号系统标注，方法是通过Layer对象的_arc_object.renderer来实现替换标注，[stackexchange](https://gis.stackexchange.com/questions/259673/how-to-change-or-assign-arcmap-layer-symbology-type-from-python)中isamson的回答启发了我，才有这个工具，非常感谢这位大神的思路启发！！！
# 介绍
提供了自定义工具箱形式和python工具箱两种，两种工具箱使用方法相同，开发环境为ArcGIS10.2.2自带的python27，工具不依赖ArcGIS自带python库外的额外的第三方库，未在其他更高版本ArcGIS环境测试。<br />写这个工具主要是我在三调和控规出图时经常需要匹配一些符号库，但有些好看的符号库只能与代码匹配，不能和名称进行匹配，出图插入符号系统很不友好，之后尝试通过ArcPy通过修改Layer的Label属性，发现了懵逼的地方，symbologyType莫名其妙被归为了OTHER，但很明显，诸如三调和控规的symbology结构完全是唯一值，不仅如此，经过测试后发现按唯一值自动添加所有值后的图层导出为.lyr后symbologyType也会莫名奇妙的变成OTHER，为了解决这个问题，制作了这个工具，给大家一个思路和方法。
