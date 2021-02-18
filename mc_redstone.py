from pyglet.gl import *
import math
import numpy as np

# blocks:(block_id)
EMPTY = 0
BLOCK = 1
REDSTONE = 2
TORCH = 3
REPEATER = 4
# 不同的方向用world_data标识
class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.world_block = list(np.zeros([1, 20, 30], dtype=int).tolist()) # world[z][y][x] 一行一行扫描，从左往右 然后一页一页 从低到高 内容为数字，对应下面的block_id   不能用 [[3.2]*30*20]！否则修改其中一个一整列都跟着变！！！！！！！！！！
        self.world_data = list(np.zeros([1, 20, 30, 5], dtype=int).tolist())  # 前4个代表四个方向是否画6x9方块 后面一个代表充能强度
        self.layer = 0
        self.mouse_press = 0  #0没有 1左键 2右键
        self.now_block = BLOCK


        pyglet.clock.schedule_interval(self.update, 1.0 / 60)  # 每秒刷新60次

    def on_draw(self):
        self.clear()
        self.draw_bg()
        self.draw_block_bg()
        self.draw_blocks()
        self.draw_text()

    def on_mouse_press(self, x, y, button, modifiers):
        if 88<x<928 and 0<y<560:
            x_ = min((x-89)//28, 29)
            y_ = min(y//28, 19)
            if button == pyglet.window.mouse.LEFT:
                self.mouse_press = 1
                self.add_block(x_, y_, self.now_block)
            elif button == pyglet.window.mouse.RIGHT:
                self.mouse_press = 2
                self.delete_block(x_, y_)


    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_press = 0

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if 88<x<928 and 0<y<560:
            x_ = (x-89)//28
            y_ = y//28
            if self.mouse_press == 1:
                self.add_block(x_, y_, self.now_block)
            elif self.mouse_press == 2:
                self.delete_block(x_, y_)

    def on_key_press(self, symbol, modifiers):
        if 0x030 < symbol < 0x035:
            self.now_block = symbol-0x030  # key.py里面0对应值为0x030


    # ------------------------------------------------------
    def test_block(self, x, y, layer, block_ids):
        # 检测某位置的方块 防止数组越界
        print(self.world_block[layer][y][x])
        if 0<=x<30 and 0<=y<20 and self.world_block[layer][y][x] in block_ids:
            return 1
        else:
            return 0

    def update_redstone_shape_around(self, x, y):
        def update_redstone_shape(x, y):
            if self.world_block[self.layer][y][x] == 2:
                block_data = self.world_data[self.layer][y][x]

                block_data[0] = self.test_block(x, y + 1, self.layer, [2, 3])
                block_data[1] = self.test_block(x + 1, y, self.layer, [2, 3])
                block_data[2] = self.test_block(x, y - 1, self.layer, [2, 3])
                block_data[3] = self.test_block(x - 1, y, self.layer, [2, 3])
                if sum(block_data) == 1:
                    if block_data[0] or block_data[2]:
                        block_data[0] = block_data[2] = 1
                    if block_data[1] or block_data[3]:
                        block_data[1] = block_data[3] = 1


                self.world_data[self.layer][y][x] = block_data

        update_redstone_shape(x, y)
        update_redstone_shape(x - 1, y)
        update_redstone_shape(x + 1, y)
        update_redstone_shape(x, y - 1)
        update_redstone_shape(x, y + 1)

    def update_redstone_energy(self, x, y):
        # surrounding包括周围的红石充能
        surrounding = []
        surrounding.append(self.test_block(x, y + 1, self.layer, [2, 3]) * self.world_data[self.layer][y + 1][x][4])
        surrounding.append(self.test_block(x + 1, y, self.layer, [2, 3]) * self.world_data[self.layer][y][x + 1][4])
        surrounding.append(self.test_block(x, y - 1, self.layer, [2, 3]) * self.world_data[self.layer][y - 1][x][4])
        surrounding.append(self.test_block(x - 1, y, self.layer, [2, 3]) * self.world_data[self.layer][y][x - 1][4])

        self.world_data[self.layer][y][x][4] = max(max(surrounding)-1, self.world_data[self.layer][y][x][4])  # 防止自己比别人大还被拉低了

    def add_block(self, x, y, block_id):
        self.world_block[self.layer][y][x] = block_id
        self.world_data[self.layer][y][x] = [0,0,0,0,0]

        if block_id == 2 or block_id == 3:  # 红石
            self.update_redstone_shape_around(x, y)


    def delete_block(self, x, y):
        block_id = self.world_block[self.layer][y][x]

        self.world_block[self.layer][y][x] = EMPTY
        if block_id == 2:  # 红石
            self.update_redstone_shape_around(x, y)

    def update(self, dt):
        # update是在init里面定义的 不是重写的
        pass


    def draw_bg(self):
        glColor3f(0.93, 0.93, 0.93)
        glBegin(GL_POLYGON)
        glVertex2f(0, 0)
        glVertex2f(1000, 0)
        glVertex2f(1000, 600)
        glVertex2f(0, 600)
        glEnd()

    def draw_block_bg(self):
        # 画(128, 128, 128)的灰色底 这样不用每个方块都画
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_POLYGON)
        glVertex2f(88, 0)
        glVertex2f(930, 0)
        glVertex2f(930, 560)
        glVertex2f(88, 560)
        glEnd()


    def draw_block(self,x , y, block_id):
        # xy指的是编号，不是坐标。
        # 一个block占28x28像素 包括边框各2像素
        # 中心方块24x24
        # 90是绘图区域距离左边的距离 左边用来显示block相关
        def draw_rectengle(x, y, place):
            # x,y 指的是起始点（整个24x24左上角xy坐标），是除去边框的坐标 程序直接加就行了
            # place 指方向，0123对应上右下左
            # 在执行之前设置颜色
            if place == 0:
                glBegin(GL_POLYGON)
                glVertex2f(x + 9, y + 24)
                glVertex2f(x + 15, y + 24)
                glVertex2f(x + 15, y + 15)
                glVertex2f(x + 9, y + 15)
                glEnd()
            if place == 1:
                glBegin(GL_POLYGON)
                glVertex2f(x + 15, y + 15)
                glVertex2f(x + 24, y + 15)
                glVertex2f(x + 24, y + 9)
                glVertex2f(x + 15, y + 9)
                glEnd()
            if place == 2:
                glBegin(GL_POLYGON)
                glVertex2f(x + 9, y)
                glVertex2f(x + 15, y)
                glVertex2f(x + 15, y + 9)
                glVertex2f(x + 9, y + 9)
                glEnd()
            if place == 3:
                glBegin(GL_POLYGON)
                glVertex2f(x, y + 15)
                glVertex2f(x + 9, y + 15)
                glVertex2f(x + 9, y + 9)
                glVertex2f(x, y + 9)
                glEnd()

        def draw_redstone(x, y, data):
            # x,y 指的是位置，（最大30x20） 程序不能直接加
            energy = self.world_data[self.layer][y][x][4]
            if energy == 0:
                glColor3f(0.5, 0, 0)
            else:
                glColor3f(0.8+0.2*energy/15, 0, 0)

            # 算出 x,y（指的是起始点（整个24x24左上角xy坐标），是除去边框的坐标）
            # 坐标起点在左下角!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            x = x*28+91
            y = y*28+1

            # 中间的一定有
            glBegin(GL_POLYGON)
            glVertex2f(x+9, y+9)
            glVertex2f(x+15, y+9)
            glVertex2f(x+15, y+15)
            glVertex2f(x+9, y+15)
            glEnd()

            for place in range(4):
                if data[place]:
                    draw_rectengle(x, y, place)

        def draw_torch(x, y, data):
            # xy指的是编号，不是坐标。
            # data 是数字
            x = x*28+91
            y = y*28+1
            def draw_point():
                glBegin(GL_POLYGON)
                glColor3f(1, 0, 0)
                for i in range(10):
                    glVertex2f(x + 12 + 6 * math.cos(2 * 3.14 / 10 * i), y + 12  + 6 * math.sin(2 * 3.14 / 10 * i))
                glEnd()

            glColor3f(0.3, 0.2, 0.1)
            for place in range(4):
                if data[place]:
                    draw_rectengle(x, y, place)

            draw_point()  # 最后画火把点 否则挡住

        if block_id == 1:  # 方块
            glColor3f(0.98, 0.98, 0)
        else:
            glColor3f(1, 1, 1)
        glBegin(GL_POLYGON)
        glVertex2f(x*28 + 1 + 90, y*28 + 1)
        glVertex2f(x*28 + 25 + 90, y*28 + 1)
        glVertex2f(x*28 + 25 + 90, y*28 + 25)
        glVertex2f(x*28 + 1 + 90, y*28 + 25)
        glEnd()

        if block_id == 2:
            draw_redstone(x, y, self.world_data[self.layer][y][x])
        elif block_id == 3:
            draw_torch(x, y, self.world_data[self.layer][y][x])

    def draw_blocks(self):
        for y in range(20):
            for x in range(30):
                self.draw_block(x, y, self.world_block[self.layer][y][x])

    def draw_text(self):
        self.text = pyglet.text.Label('', font_name='Arial', font_size=15,
                                       x=5, y=self.height - 50, width=88, anchor_x='left', anchor_y='top', multiline=True, color=(0,0,0,255))
        self.text.text = '1\n方块\n\n2\n红石\n\n3\n火把\n\n4\n中继器\n\n\n现在\n'+['方块', '红石', '火把', '中继器'][self.now_block-1]
        self.text.draw()




window = Window(width=1000, height=600, caption='Pyglet', resizable=False)
pyglet.app.run()
# 30x20
# window坐标起点在左下角!!!!!!!!!!

# 世界的数据分为两类：self.world_block  self.world_data
#                用于储存是哪个方块   用于储存方块对应数据
# 存在的bug:红石线遇到火把不拐弯  # 已经修复

