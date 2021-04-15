# Redstone-Circuit-Simulator
[![Author_page](https://img.shields.io/badge/Author%20page-on%20bilibili-green)](https://space.bilibili.com/290472819)

红石电路模拟器

## 目录
* [环境](#环境)
* [运行](#运行)
* [运行示例截图](#运行示例)
* [物品与功能](#物品/功能)
* [更新日志](#物品/功能)

## 环境
  - Python3
  - pyglet库
  - numpy库  # 未来可能会改bug，然后就不用numpy来创建列表了

## 运行
  - 配置好环境后运行mc_redstone.py
  - 使用键盘上数字键切换方块，左键放置右键删除
  - 可按住鼠标拖动进行批量放置

### 运行示例

示例1：1字节红石内存
> 储存的内容为 01001011

![example1](https://raw.githubusercontent.com/baoqi-zhong/Redstone-Circuit-Simulator/main/example.png)

---
示例2：红石实现XOR运算

![example2](https://raw.githubusercontent.com/baoqi-zhong/Redstone-Circuit-Simulator/main/example2.png)

## 物品/功能
- 物品
    - [x] 方块
    - [x] 红石线
    - [x] 红石火把
    - [ ] 中继器
    - [ ] 拉杆
    - [ ] 红石灯
    
- 功能
    - [x] 红石火把非门
    - [x] 红石火把1tick延迟
    - [x] 双层布线
    - [x] 弱充能
    - [ ] 强充能
    - [ ] 无限地图
    - [X] 地图保存/加载
    


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
    
    2021.2.27
    实现了两层布线，修改红石线遇到红石火把不拐弯的问题
    (加50行实现了两层运行逻辑 针不戳
    
    2021.4.15
    实现地图保存加载

未来计划

    中继器及强充能
    拉杆、红石灯等方块
    无限地图
    3D视图
    
    在模拟器中建一个CPU
    
---
最后，祝大家好运\\(≧▽≦)/
---
last update:2021.4.15
