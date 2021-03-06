# NS by Example 代码

本来以为这个教程不推荐, 因为ns版本过低, 代码位置不够准确
结果, 这个文档就是不错的了, 其他文档更老旧, 真是古董一样的 ns2 啊~

(在某个不起眼的地方注明了在 (Tested with ns-2.1b8a, ns-2.1b9a and ns-2.26 测试通过 )

Source: http://nile.wpi.edu/NS/


执行程序前先 `cd output` 进入目录, 将生成文件留在 `output` 目录中便于跳过git版本管理

- Basics 基础
  * OTcl: The User Language
    + basic01: `ns ../basic01_ex-tcl.tcl` 简单的数学运算 (pow /mod) 例子
    + basic02: `ns ../basic02_ex-otcl.tcl` 简单的类 (Mom & Kid)
  * Simple Simulation Example
    + basic03: `ns ../basic03_ns-simple.tcl` 简单 simulation 拓扑(4个节点)例子, 生成 `out.nam`
       * 需要安装 `nam` 并激活 xwindows (MacOSX: SqureZ)
- Post Simulation 结果分析
  * Trace Analysis Example
    + post01: `ns ../post01_ns-simple-trace.tcl` 写入 trace 文件 `out.tr` [文件格式说明](http://nile.wpi.edu/NS/analysis.html)
      + `../post01_trace2jitter.sh jitter10.txt` 通过 `out.tr` 生成抖动数据文件
      + 将抖动数据文件可视化绘制 plot
        * Mac 下用: `../../../ns3/scratch/my_plot_helper.py jitter10.txt` 
        * Linux下难看但是简单一点: `xgraph jitter10.txt` 
    + post02: `ns ../post02_red.tcl` 对 RED 队列进行监控, 并使用 xgraph 直接绘制结果. 在数据文件`temp.queue`中存储了两个数据 queue/ave_queue 并进行绘图.
  * Trace Analysis Utilities
      + `column.sh` `stats.pl` `jitter.sh`

- Extending NS :
  - 下面扩展代码的通用步骤包括:
    * `cd ns-2.35;`, 在 `Makefile` 的 `OBJ_CC` 的最后一行追加 `youcode.o \ $(OBJ_STL)`, 对应复制过去 `yourcode.cc`
    * 执行 `make` 编译. 需要时执行 `make clean;`
    * 执行 `ns your-ex.tcl` 测试
  * OTcl Linkage:
    + 扩展代码 Makefile 在 OBJ_CC 最后一行追加 `ex-linkage.o \ $(OBJ_STL)` ,
    + 复制代码 `cp ../ex-linkage.cc /opt/coding/ns-allinone-2.35/ns-2.35/`, `make` 进行编译
    + 执行脚本 `ns ../ex-linkage.tcl`
  * Add New Application and Agent
    + `cp ../udp-mm.cc ../udp-mm.h ../mm-app.cc ../mm-app.h /opt/coding/ns-allinone-2.35/ns-2.35/`
    + 按教程需要修改 5 处代码, 参 [文档](http://nile.wpi.edu/NS/new_app_agent.html) [github代码](https://github.com/chenzheng128/ns-allinone-2.35/commit/5015896cdcd3bee620da6ee3a01a376f4b4ed244)
    + `ns ../ex-mm-app.tcl` 执行测试
  * Add New Queue
    + `output $ cp ../dtrr-queue.cc ../dtrr-queue.h  /opt/coding/ns-allinone-2.35/ns-2.35/`
    +  参 [github代码](https://github.com/chenzheng128/ns-allinone-2.35/commit/971539d36cfd5701d8cdd6a2862c663a11f90188)
    +  `ns ../ex-dtrr-queue.tcl` 执行测试
- More Examples : 
  + LAN: 运行失败, 错误 invalid command name "Mac/Csma/Ca". mac-csma.cc 未编译. 但加上 `mac/mac-csma.o` 还是有很多编译错误
  + Multicasting : 修改兼容 2.35 `ex-mcast.tcl`
  + Web Server: 修改兼容 2.35 `ex-web.tcl`

几个可参考的拓扑图

![Figure 2. C++ and OTcl: The Duality](http://nile.wpi.edu/NS/Figure/fig2.gif)

![Figure 3. Architectural View of NS](http://nile.wpi.edu/NS/Figure/fig3.gif)
