##  Autovisor

智慧树视频课辅助脚本，开启挂机摸鱼时代~

**新学期必备干货, 建议收藏备用 !!**

**Github项目主页：**[CXRunfree/Autovisor](https://github.com/CXRunfree/Autovisor)

------

#### 2024/9/22 fixed-3.14.2 更新

-  修复了进入课程**界面异常**退出的bug;
-  修复了正常结束时的报错问题;
-  修复了旧版本存在的播放完成后多跳过一集的问题；
-  此次更新将程序重构为**异步架构**，使用**协程**处理视频播放、弹题检测和安全验证;
-  避免了主线程阻塞造成的卡死问题，提高了程序的响应性;
-  显著提升弹窗检测频率，减少了因弹窗导致程序卡死的情况。

------

#### 一、程序介绍:

**项目简介：**

这是一个可无人监督的自动化程序，基于微软的Playwright框架，由Python和JavaScript编写而成；相对于常见的油猴脚本，本程序可有效防止被网页检测。核心原理是使浏览器模拟用户的点击操作。

**程序功能:**

- 可以快速登录
- **自动播放和切换下一集**
- **跳过弹窗和弹出的题目**
- **自动静音、调整1.8倍速**
- **检测视频是否暂停并续播**
- 检测当前学习进度并后台实时更新
- 根据当前时间自动设置背景颜色(白昼/暗夜)
- 加入了定时模拟鼠标滑动功能 (减少被检测到的概率)
- 完成章节时将提示已刷课时长

#### 二、使用须知:

1.请确保系统为windows10及以上

2.文件夹内有 **configs.ini文件** (可能没显示 **.ini**后缀名)，请用文本编辑器打开;

3.填写配置文件

- 默认启动Edge(win10及以上自带), 也可指定为Chrome
- 文件里的**EXE_PATH项**可自定义浏览器路径, 但必须精确到**浏览器可执行文件的位置**;

​    若不填此项, 就会启动位于系统默认位置的浏览器。

​    (不知浏览器的安装路径? 请看下方 **四、常见问题 ** )

4.根据文件内的说明填写好配置信息，一定要**保存后**再退出。

**注意：**所有配置项都不加引号.

<img src="https://img-blog.csdnimg.cn/direct/52a0d66b345b437abc476cb2036e1117.png">



4.运行 **Autovisor.exe**，会自动打开浏览器，登录界面的滑块验证请**手动完成**，进入网课界面后就能自动刷课了 !

------

#### **三、发行版下载:**

Github: [Releases · CXRunfree/Autovisor (github.com)](https://github.com/CXRunfree/Autovisor/releases)

网盘备用: [[蓝奏云\] Autovisor-for-windows](https://wwk.lanzouj.com/b05evsxif) 密码:492l

这是已经打包好的程序, 若需要**源代码**自行请前往Github项目主页下载.

#### 四、常见问题 :

1.为什么会出现一个命令行黑框?

- 这是程序运行的后台，你可以查看当前运行的状态

2.为什么网页一片空白/无法加载课程界面,一段时间后程序就退出了?

- 大概率你在配置文件里填入的**课程链接有误**;

3.为什么运行程序只出现后台却没出现浏览器界面？

- 只要后台未异常退出就不必担心; 如果出错可能是你的浏览器安装路径有问题

4.我想自定义要启动的浏览器, 但是找不到装在哪里? 

- 打开你的浏览器, 在地址栏中输入 Chrome://version 回车之后, 如图的"可执行文件目录" 就是浏览器安装目录了。

  <img src="https://img-blog.csdnimg.cn/direct/aec0acdfd3b946069f5edb31f9191591.png">

5.关于弹题关不掉/程序卡住的问题:

- 因为弹题是时刻有可能发生的, 而弹题检测不是时刻都进行, 所以这个问题不能完全消除;
- 3.14以上版本使用 异步+协程 进行弹题检测，目前效果非常好，建议更新使用。

------

**已知Bug:**

- **长时间挂机**有概率弹出人机验证, 程序检测到后会暂停刷课，直到手动验证完成;
- 若出现其他异常崩溃，请提交issue并附上日志文件log.txt的信息, 或者在CSDN发私信给我;

**碎碎念:**

觉得体验还不错? 来给项目发电支持一下吧~!

(其实作者也要吃饭的 ^-^)

<img src="https://img-blog.csdnimg.cn/direct/2d94a77c4bf643c1bff1712461c4f1bf.png" alt="img" style="zoom: 50%;" />

**作者的CSDN:** [Runfreeone 欢迎关注~](https://blog.csdn.net/Runfreeone)

**注意：本程序只可用于学习和研究计算机原理**

还等什么? 快开始愉快的刷课吧~ !
