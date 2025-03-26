**这次我改了文件格式，配置文件都在config文件夹内**

极大的美观了界面（好欸！！！）

并且这次可以支持播放图片力，至于播放音乐啥的之后再说awa

danmaku.txt中更改弹幕显示

danmaku_config.txt是索引，速度以及弹幕数量在其中更改，分别是speed_range和max_count

colors.txt中更改颜色，支持RGB格式和16进制颜色码

image_config.txt是图片显示索引
dir后面为图片存放文件夹
speed_range移动速度
scale_range图片大小
max_count一次性最大图片张数

fonts文件夹中放入字体文件.ttf或.ttc

***config.json中写入字体文件，可以直接用记事本打开，注意每一段后面都要打逗号，如果是最后一段则不需要***

**Windows系统自带的字体路径**
C:/Windows/Fonts/msyh.ttc

~~可以直接写在json文件中写入,例如{"K_1": "C:/Windows/Fonts/msyh.ttc"}~~
字体切换改成按F键啦!在config.json内你可以这么编写

{"font": {"paths": ["fonts/ew.ttf"],"size": 30}}

又或者

{"font": {"paths": ["C:/Windows/Fonts/msyh.ttc"],"size": 30}}

但是请注意，一定要在末尾加上逗号，除非是最后一个

{"font": {"paths": ["fonts/ew.ttf","C:/Windows/Fonts/msyh.ttc"],"size": 30}}

**MacOS**
路径为/System/Library/Fonts/STHeiti Medium.ttc

**文件运行点击danmu1.2.exe**