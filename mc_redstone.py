from pyglet.gl import *
from pyglet.window import key
import math
import numpy as np
import time
import os


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
        self.world_block = list(np.zeros([2, 20, 30], dtype=int).tolist()) # world[z][y][x] 一行一行扫描，从左往右 然后一页一页 从低到高 内容为数字，对应下面的block_id   不能用 [[3.2]*30*20]！否则修改其中一个一整列都跟着变！！！！！！！！！！
        self.world_data = list(np.zeros([2, 20, 30, 5], dtype=int).tolist())  # 前4个代表四个方向是否画6x9方块 后面一个代表充能强度

        self.layer = 0
        self.mouse_press = 0  #0没有 1左键 2右键
        self.now_block = BLOCK
        self.next_tick_update = []  # 坐标+插在的方块的充能状态

        self.last_focus = [0, 0]



        pyglet.clock.schedule_interval(self.update, 1.0 / 10)  # 每秒刷新60次

    def on_draw(self):
        self.clear()
        self.draw_bg()
        self.draw_block_bg()
        self.draw_blocks()
        self.draw_text()

        #self.debug()

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
            x_ = min((x - 89) // 28, 29)
            y_ = min(y // 28, 19)
            if [x_, y_] != self.last_focus:
                if self.mouse_press == 1:
                    self.add_block(x_, y_, self.now_block)
                elif self.mouse_press == 2:
                    self.delete_block(x_, y_)

                self.last_focus = [x_, y_]

    def on_key_press(self, symbol, modifiers):
        if 0x030 < symbol < 0x035:
            self.now_block = symbol-0x030  # key.py里面0对应值为0x030
        elif symbol == key.S:
            self.save()
        elif symbol == key.L:
            self.load()
    
             

    # ------------------------------------------------------

    def test_block(self, x, y, layer, block_ids):
        # 检测某位置的方块 防止数组越界
        if 0 <= x < 30 and 0 <= y < 20 and 0<= layer < len(self.world_block) and self.world_block[layer][y][x] in block_ids:
            return 1
        else:
            return 0

    def update_redstone_shape_around(self, x, y):
        # 不用传入layer 因为不管是哪一层修改了都有可能影响到其他层。所以所有层都要check
        def update_redstone_shape(x, y, layer):
            # 防止越界
            if 0 <= x < 30 and 0 <= y < 20 and 0 <= layer < len(self.world_block[0]) and self.world_block[layer][y][x] == REDSTONE:
                block_data = self.world_data[layer][y][x]  # 不能改成[0,0,0,0,0]因为要继承充能强度

                block_data[0] = min(self.test_block(x, y + 1, layer, [REDSTONE, TORCH]) + self.test_block(x, y + 1, layer - 1, [REDSTONE]) + self.test_block(x, y + 1, layer + 1, [REDSTONE]), 1)
                block_data[1] = min(self.test_block(x + 1, y, layer, [REDSTONE, TORCH]) + self.test_block(x + 1, y, layer - 1, [REDSTONE]) + self.test_block(x + 1, y, layer + 1, [REDSTONE]), 1)
                block_data[2] = min(self.test_block(x, y - 1, layer, [REDSTONE, TORCH]) + self.test_block(x, y - 1, layer - 1, [REDSTONE]) + self.test_block(x, y - 1, layer + 1, [REDSTONE]), 1)
                block_data[3] = min(self.test_block(x - 1, y, layer, [REDSTONE, TORCH]) + self.test_block(x - 1, y, layer - 1, [REDSTONE]) + self.test_block(x - 1, y, layer + 1, [REDSTONE]), 1)
                if sum(block_data[:4]) == 1:
                    if block_data[0] or block_data[2]:
                        block_data[0] = block_data[2] = 1
                    if block_data[1] or block_data[3]:
                        block_data[1] = block_data[3] = 1

                self.world_data[layer][y][x] = block_data

        update_redstone_shape(x, y, self.layer)
        update_redstone_shape(x, y, self.layer + 1)  # 自己上下也要判断 因为不知道自己是第几层
        update_redstone_shape(x, y, self.layer - 1)

        update_redstone_shape(x, y + 1, self.layer)
        update_redstone_shape(x, y + 1, self.layer + 1)
        update_redstone_shape(x, y + 1, self.layer - 1)

        update_redstone_shape(x + 1, y, self.layer)
        update_redstone_shape(x + 1, y, self.layer + 1)
        update_redstone_shape(x + 1, y, self.layer - 1)

        update_redstone_shape(x, y - 1, self.layer)
        update_redstone_shape(x, y - 1, self.layer + 1)
        update_redstone_shape(x, y - 1, self.layer - 1)

        update_redstone_shape(x - 1, y, self.layer)
        update_redstone_shape(x - 1, y, self.layer + 1)
        update_redstone_shape(x - 1, y, self.layer - 1)

    def update_redstone_energy(self):
        # 要改 只更新影响的位置
        flag = False
        for layer in range(self.layer, self.layer+2):
            for y in range(20):
                for x in range(30):
                    if self.world_block[layer][y][x] == REDSTONE:
                        surrounding = []

                        if y + 1 < 20:
                            surrounding.append(self.test_block(x, y + 1, layer, [REDSTONE, TORCH]) * self.world_data[layer][y + 1][x][4])
                            if layer + 1 < len(self.world_data):
                                surrounding.append(self.test_block(x, y + 1, layer + 1, [REDSTONE]) * self.world_data[layer + 1][y + 1][x][4])
                            if layer - 1 >= 0:
                                surrounding.append(self.test_block(x, y + 1, layer - 1, [REDSTONE]) * self.world_data[layer - 1][y + 1][x][4])
                        if x + 1 < 30:
                            surrounding.append(self.test_block(x + 1, y, layer, [REDSTONE, TORCH]) * self.world_data[layer][y][x + 1][4])
                            if layer + 1 < len(self.world_data):
                                surrounding.append(self.test_block(x + 1, y, layer + 1, [REDSTONE]) * self.world_data[layer + 1][y][x + 1][4])
                            if layer - 1 >= 0:
                                surrounding.append(self.test_block(x + 1, y, layer - 1, [REDSTONE]) * self.world_data[layer - 1][y][x + 1][4])
                        if y - 1 >= 0:
                            surrounding.append(self.test_block(x, y - 1, layer, [REDSTONE, TORCH]) * self.world_data[layer][y - 1][x][4])
                            if layer + 1 < len(self.world_data):
                                surrounding.append(self.test_block(x, y - 1, layer + 1, [REDSTONE]) * self.world_data[layer + 1][y - 1][x][4])
                            if layer - 1 >= 0:
                                surrounding.append(self.test_block(x, y - 1, layer - 1, [REDSTONE]) * self.world_data[layer - 1][y - 1][x][4])
                        if x - 1 >= 0:
                            surrounding.append(self.test_block(x - 1, y, layer, [REDSTONE, TORCH]) * self.world_data[layer][y][x - 1][4])
                            if layer + 1 < len(self.world_data):
                                surrounding.append(self.test_block(x - 1, y, layer + 1, [REDSTONE]) * self.world_data[layer + 1][y][x - 1][4])
                            if layer - 1 >= 0:
                                surrounding.append(self.test_block(x - 1, y, layer - 1, [REDSTONE]) * self.world_data[layer - 1][y][x - 1][4])

                        if self.world_data[layer][y][x][4] != max(max(surrounding)-1, 0):
                            self.world_data[layer][y][x][4] = max(max(surrounding)-1, 0)
                            flag = True
        if flag:
            self.update_redstone_energy()

    def update_torch_around(self, x, y):
        if not self.test_block(x, y + 1, self.layer, [BLOCK]):
            # 这里的1 in 不能去掉，因为要利用and屏蔽特性保证后面index函数不报错
            if self.test_block(x, y + 1, self.layer, [TORCH]) and 1 in self.world_data[self.layer][y + 1][x][:4] and \
                    self.world_data[self.layer][y + 1][x][:4].index(1) == 2:
                self.delete_block(x, y + 1)
            if self.test_block(x + 1, y, self.layer, [TORCH]) and 1 in self.world_data[self.layer][y][x + 1][:4] and \
                    self.world_data[self.layer][y][x + 1][:4].index(1) == 3:
                self.delete_block(x + 1, y)
            if self.test_block(x, y - 1, self.layer, [TORCH]) and 1 in self.world_data[self.layer][y - 1][x][:4] and \
                    self.world_data[self.layer][y - 1][x][:4].index(1) == 0:
                self.delete_block(x, y - 1)
            if self.test_block(x - 1, y, self.layer, [TORCH]) and 1 in self.world_data[self.layer][y][x - 1][:4] and \
                    self.world_data[self.layer][y][x - 1][:4].index(1) == 1:
                self.delete_block(x - 1, y)

    def update_torch_energy(self):
        for data in self.next_tick_update:
            if self.world_block[data[2]][data[1]][data[0]] == TORCH:
                if data[3] == 1:  # 方块弱充能
                    self.world_data[data[2]][data[1]][data[0]][4] = 0
                else:
                    self.world_data[data[2]][data[1]][data[0]][4] = 16

        self.next_tick_update = []  # 火把的x,y,z,火把插在方块的充能情况
        for layer in range(self.layer, self.layer+2):
            for y in range(20):
                for x in range(30):
                    # 如果自己是火把并且不是插在地上
                    if self.world_block[layer][y][x] == TORCH:
                        if sum(self.world_data[layer][y][x][:4]) > 0:
                            # 如果火把指向上
                            if self.world_data[layer][y][x][0]:
                                self.next_tick_update.append([x, y, layer, self.world_data[layer][y + 1][x][4]])
    
                            if self.world_data[layer][y][x][1]:
                                self.next_tick_update.append([x, y, layer, self.world_data[layer][y][x + 1][4]])
    
                            if self.world_data[layer][y][x][2]:
                                self.next_tick_update.append([x, y, layer, self.world_data[layer][y - 1][x][4]])
    
                            if self.world_data[layer][y][x][3]:
                                self.next_tick_update.append([x, y, layer, self.world_data[layer][y][x - 1][4]])
                        else:
                            if layer != self.layer:
                                self.next_tick_update.append([x, y, layer, self.world_data[self.layer][y][x][4]])

    def update_block_energy(self):
        # 待会强充能要改红石那里的代码，
        for y in range(20):
            for x in range(30):
                if self.world_block[self.layer][y][x] == BLOCK:
                    # 如果四周有红石，且方向正确且有充能
                    # 红石对方块弱充能1 中继器可以强充能16
                    if self.test_block(x, y + 1, self.layer, [REDSTONE]) and self.world_data[self.layer][y + 1][x][:4] == [1, 0, 1, 0] and \
                            self.world_data[self.layer][y + 1][x][4] > 0:
                        self.world_data[self.layer][y][x][4] = 1
                    elif self.test_block(x + 1, y, self.layer, [REDSTONE]) and self.world_data[self.layer][y][x + 1][:4] == [0, 1, 0, 1] and \
                            self.world_data[self.layer][y][x + 1][4] > 0:
                        self.world_data[self.layer][y][x][4] = 1
                    elif self.test_block(x, y - 1, self.layer, [REDSTONE]) and self.world_data[self.layer][y - 1][x][:4] == [1, 0, 1, 0] and \
                            self.world_data[self.layer][y - 1][x][4] > 0:
                        self.world_data[self.layer][y][x][4] = 1
                    elif self.test_block(x - 1, y, self.layer, [REDSTONE]) and self.world_data[self.layer][y][x - 1][:4] == [0, 1, 0, 1] and \
                            self.world_data[self.layer][y][x - 1][4] > 0:
                        self.world_data[self.layer][y][x][4] = 1
                    elif self.test_block(x, y, self.layer + 1, [REDSTONE]) and self.world_data[self.layer + 1][y][x][4] > 0:
                        self.world_data[self.layer][y][x][4] = 1

                    else:
                        self.world_data[self.layer][y][x][4] = 0

    def add_block(self, x, y, block_id):
        # addblock指的是在坐标添加，添加到哪一层由addblock自己判断
        def find_torch_ok_list(x, y):
            ok_list = []
            if self.test_block(x, y + 1, self.layer, [1]):
                ok_list.append(0)
            if self.test_block(x + 1, y, self.layer, [1]):
                ok_list.append(1)
            if self.test_block(x, y - 1, self.layer, [1]):
                ok_list.append(2)
            if self.test_block(x - 1, y, self.layer, [1]):
                ok_list.append(3)
            return ok_list


        if block_id == BLOCK:
            self.world_block[self.layer][y][x] = BLOCK
        elif block_id == TORCH:
            if self.world_block[self.layer][y][x] != BLOCK:
                if self.world_block[self.layer][y][x] == block_id:
                    ok_list = find_torch_ok_list(x, y)
                    if ok_list:
                        if sum(self.world_data[self.layer][y][x][:4]) == 0:
                            self.world_data[self.layer][y][x][ok_list[0]] = 1

                        else:

                            this = ok_list.index(self.world_data[self.layer][y][x].index(1))  # 当前状态对应ok_list中的第几个
                            self.world_data[self.layer][y][x][ok_list[this]] = 0
                            if this+1 < len(ok_list):
                                self.world_data[self.layer][y][x][ok_list[this+1]] = 1
                else:
                    self.world_data[self.layer][y][x][:4] = [0, 0, 0, 0]
                    self.world_data[self.layer][y][x][4] = 16
                    self.world_block[self.layer][y][x] = block_id
            else:
                self.world_block[self.layer + 1][y][x] = TORCH
                self.world_data[self.layer + 1][y][x] = [0, 0, 0, 0, 16]
            self.update_redstone_shape_around(x, y)  # 只会动rs
            self.update_redstone_energy()



        elif block_id == REDSTONE:
            if self.world_block[self.layer][y][x] != BLOCK:
                self.world_block[self.layer][y][x] = REDSTONE

            else:
                self.world_block[self.layer+1][y][x] = block_id
            self.update_redstone_shape_around(x, y)  # 只会动rs
            self.update_redstone_energy()



    def delete_block(self, x, y):
        if self.test_block(x, y, self.layer+1, [TORCH, REDSTONE]):
            self.world_block[self.layer+1][y][x] = EMPTY
            self.world_data[self.layer+1][y][x] = [0, 0, 0, 0, 0]
            self.update_redstone_shape_around(x, y)
            self.update_redstone_energy()
        else:
            update_redstone_shape_flag = False
            if self.world_block[self.layer][y][x] in [REDSTONE, TORCH]:
                update_redstone_shape_flag = True
            if self.world_block[self.layer][y][x] == BLOCK:
                self.update_torch_around(x, y)

            self.world_block[self.layer][y][x] = EMPTY
            self.world_data[self.layer][y][x] = [0, 0, 0, 0, 0]
            if update_redstone_shape_flag:
                self.update_redstone_shape_around(x, y)
                self.update_redstone_energy()

    def update(self, dt):
        # update是在init里面定义的 不是重写的
        #self.update_redstone_energy()

        self.update_block_energy()
        self.update_torch_energy()
        self.update_redstone_energy()
        self.update_block_energy()
        self.update_torch_energy()
        self.update_redstone_energy()
        #self.debug()

        #print(self.world_block[self.layer][0][0], self.world_block[self.layer+1][0][0], )

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

    def draw_block(self, x , y, layer, clear=True):
        # xy指的是编号，不是坐标。
        # 一个block占28x28像素 包括边框各2像素
        # 中心方块24x24
        # 90是绘图区域距离左边的距离 左边用来显示block相关
        # draw_block是一层一层画的
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

        def draw_redstone(x, y):
            # x,y 指的是位置，（最大30x20） 程序不能直接加
            data = self.world_data[layer][y][x]

            if data[4] == 0:
                glColor3f(0.5, 0, 0)
            else:
                glColor3f(0.8+0.2*data[4]/15, 0, 0)

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

        def draw_torch(x, y):
            # xy指的是编号，不是坐标。
            data = self.world_data[layer][y][x]

            def draw_point():
                if self.world_data[layer][y][x][4] == 16:
                    glColor3f(1, 0, 0)
                else:
                    glColor3f(0.5, 0, 0)
                glBegin(GL_POLYGON)
                for i in range(10):
                    glVertex2f(x*28+91 + 12 + 6 * math.cos(2 * 3.14 / 10 * i), y*28+1 + 12 + 6 * math.sin(2 * 3.14 / 10 * i))
                glEnd()

            glColor3f(0.3, 0.2, 0.1)
            for place in range(4):
                if data[place]:
                    draw_rectengle(x*28+91, y*28+1, place)

            draw_point()  # 最后画火把点 否则挡住

        block_id = self.world_block[layer][y][x]
        if clear:
            if block_id == BLOCK:  # 方块
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
            draw_redstone(x, y)
        elif block_id == 3:
            draw_torch(x, y)

    def draw_blocks(self):
        for layer in range(self.layer, self.layer + 2):
            for y in range(20):
                for x in range(30):
                    self.draw_block(x, y, layer, clear=True if layer == self.layer else False)

    def draw_text(self):
        self.text = pyglet.text.Label('', font_name='Arial', font_size=15,
                                       x=5, y=self.height - 50, width=88, anchor_x='left', anchor_y='top', multiline=True, color=(0,0,0,255))
        self.text.text = '1\n方块\n\n2\n红石\n\n3\n火把\n\n4\n中继器\n\n\n现在\n'+['方块', '红石', '火把', '中继器'][self.now_block-1]
        self.text.draw()


    def save(self):
        try:
            save_data = np.array([self.world_block, self.world_data])
            np.save("world_data", save_data)
            print("success")
        except:
            print("加载失败文件损坏")

    def load(self):
        if os.path.exists("./world_data.npy"):
            try:
                save_data = np.load("world_data.npy",allow_pickle=True).tolist()
                self.world_block = save_data[0]
                self.world_data = save_data[1]
                print("success")
            except:
                print("加载失败文件损坏")
        else:
            print("文件不存在")
        

    def debug(self):
        print(self.world_data[0][1][0],self.world_data[1][1][0])
        #[pyglet.text.Label(str(self.world_data[self.layer][y][x][4]), font_size=15, x=x * 28 + 91, y=y* 28 + 1, width=28, color=(0,0,0,255)).draw() for x in range(6) for y in range(6)]


if __name__ == '__main__':
    window = Window(width=1000, height=600, caption='Pyglet', resizable=False)
    pyglet.app.run()
# 30x20
# window坐标起点在左下角!!!!!!!!!!

# 世界的数据分为两类：self.world_block  self.world_data
#                用于储存是哪个方块   用于储存方块对应数据

# 目前只有2层，第二层只能放红石和火把
