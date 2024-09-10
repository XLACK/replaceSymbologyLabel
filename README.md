# 替换符号系统标注
使用arcpy实现替换符号系统标注，方法是通过Layer对象的_arc_object.renderer来实现替换标注，[stackexchange](https://gis.stackexchange.com/questions/259673/how-to-change-or-assign-arcmap-layer-symbology-type-from-python)中isamson的回答启发了我，才有这个工具，非常感谢这位大神的思路启发！！！
# 介绍
提供了自定义工具箱形式和python工具箱两种，两种工具箱使用方法相同，开发环境为ArcGIS10.2.2自带的python27，工具不依赖ArcGIS自带python库外的额外的第三方库，未在其他更高版本ArcGIS环境测试。<br />写这个工具主要是我在三调和控规出图时经常需要匹配一些符号库，但有些好看的符号库只能与代码匹配，不能和名称进行匹配，出图插入符号系统很不友好，之后尝试通过ArcPy修改Layer的Label属性，发现了懵逼的地方，symbologyType莫名其妙被归为了OTHER，但很明显，诸如三调和控规的symbology结构完全是唯一值特征，不仅如此，经过测试后发现按唯一值自动添加所有值后的图层导出为“.lyr”后，symbologyType也会莫名奇妙的变成OTHER，为了解决这个问题，制作了这个工具，给大家一个思路和方法来操作symbologyType。
# 使用
工具执行前的图层
<br />![image](https://github.com/XLACK/replaceSymbologyLabel/blob/main/markdown_jpg/runToolBefore.jpg)
<br />工具界面，工具内部已对细节进行了描述，可以在工具内部查看提示信息
<br />![image](https://github.com/XLACK/replaceSymbologyLabel/blob/main/markdown_jpg/toolview.jpg)
<br />工具执行后的图层样式
<br />![image](https://github.com/XLACK/replaceSymbologyLabel/blob/main/markdown_jpg/runToolAfter.jpg)
# 注意
1.为了工具友好，所以在toolValidator部分花费了比较大的篇幅，我知道这可能违背了ArcToolBox的初衷和规范，但ESRI并没有为ArcPy提供对ArcObject更加原子化的操作，工具能进行的操作实际也能有限，为尽可能减少误输入的可能性，所以尽可能把错误排查在执行前；<br />
2.工具的具体使用方法在工具箱内部文档有详细说明，工具实际并没有对所有危险操作进行错误提示，留有一部分余地方便进行自定义匹配，但会对这些操作进行警告，具体情况可以自行操作尝试或阅读源码；<br />
3.推荐使用python工具箱的实现，因为工具内部会对字段值进行遍历，而自定义工具箱遍历采用的是SearchCursor方式进行遍历，实测对于地类图斑这一类大型数据访问速度很慢，且卡顿严重，为提高效率在python工具箱中改为采用numpy数组进行遍历，实测效率有很大的提升，后续有空会对自定义工具箱进行更新。
