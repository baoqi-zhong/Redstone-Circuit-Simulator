# Redstone-Circuit-Simulator
[![Author_page](https://img.shields.io/badge/Author%20page-on%20bilibili-green)](https://space.bilibili.com/290472819)

红石电路模拟器

## 更新日志
#### 实现了红石火把非门，建立tick更新机制

    2021.2.18
    建立基本操作界面、操作逻辑，完成了平面红石布线逻辑
    
    2021.2.18
    完成了红石线运行逻辑
    
    2021.2.18
    完成了红石火把运行逻辑，修正了越界、形状不更新的bug。
    未实现红石火把非门及强弱充能。
    (一个下午写300行代码，改不下30个bug
    
    2021.2.18
    改越界，红石形状错误bug，实现了红石火把非门及弱充能，建立tick更新机制。
    未实现强充能及中继器
    (400行庆祝

未来计划

    中继器及强充能
    拉杆、红石灯等方块
    地图保存
    无限地图
    多层布线、多层预览
    跨层布线
    3D视图
    
    在模拟器中建一个CPU
    
    
    
***

## 环境
  - Python3
  - pyglet库
  - numpy库  # 未来可能会改bug，然后就不用numpy来创建列表了

## 运行
  - 配置好环境后运行mc_redstone.py
  - 使用键盘上数字键切换方块，左键放置右键删除
  - 可按住鼠标拖动进行批量放置

> 运行示例

图示为1字节红石内存
> 储存的内容为 01001011
![example1](https://raw.githubusercontent.com/baoqi-zhong/Redstone-Circuit-Simulator/main/example.png)

最后，祝大家好运\\(≧▽≦)/
---
last update:2021.2.19
