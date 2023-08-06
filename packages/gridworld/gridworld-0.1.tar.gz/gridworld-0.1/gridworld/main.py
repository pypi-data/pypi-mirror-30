import arcade
import pyglet.image  # what is this for?
import arcade
import numpy as np
import time
from numpy import random

## adapted from the arcade examples

# Set how many rows and columns we will have
ROW_COUNT = 60
COLUMN_COUNT = 60

# This sets the margin between each cell
# and on the edges of the screen.
MARGIN = 0

ACTION_PROFILE = {0: [-1, 0], 1: [0, 1], 2: [0, -1], 3: [1, 0]}

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = (600)
SCREEN_HEIGHT = (600)
WIDTH = int((SCREEN_WIDTH - MARGIN)/COLUMN_COUNT - MARGIN)
HEIGHT = int((SCREEN_HEIGHT - MARGIN)/ROW_COUNT - MARGIN)
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN + 1  # the 1 is for a little extra padding.


class Gridworld(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        # grid is simply a numpy ndarray
        self.grid = np.zeros(shape=(ROW_COUNT, COLUMN_COUNT))
        arcade.set_background_color((200, 200, 200))
        self.agent = Agent(0, 0)
        # self.reward = Reward(int(.9*COLUMN_COUNT), int(0.9*ROW_COUNT))
        self.reward = Reward(5, 5)
        self.entities = [self.agent, self.reward]
        self.draw_desirability_fn = False
        self.stopped = False
        self.do_reset = False
        self.draw_grid = True
        self.speed = 0.9

    def on_draw(self):
        arcade.start_render()
        # Draw the grid
        if self.draw_desirability_fn:
            baseline = np.array([200, 200, 200]) # a nice grey for cost of 1
            for row in range(ROW_COUNT):
                for column in range(COLUMN_COUNT):
                    # low costs should be green.
                    color = baseline #+ self.grid[row, column]
                    x, y = Gridworld.get_xy_from_Cell_idx(row, column)
                    arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)
        for entity in self.entities:
            x, y = Gridworld.get_xy_from_Cell_idx(entity.coord[0], entity.coord[1])
            arcade.draw_rectangle_filled(x, y, entity.scale*WIDTH, entity.scale*HEIGHT, entity.color)
        if self.draw_grid:
            for i in range(ROW_COUNT+1):
                y = i*HEIGHT
                arcade.draw_line(0, y, SCREEN_WIDTH, y, color=arcade.color.BLACK)
            for j in range(COLUMN_COUNT+1):
                x = j*WIDTH
                arcade.draw_line(x, 0, x, SCREEN_HEIGHT, color=arcade.color.BLACK)


    @staticmethod
    def get_xy_from_Cell_idx(row, column):
        x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
        y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2
        return x, y

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.end()
        elif key == arcade.key.ENTER:
            self.reset()
        elif key == arcade.key.SPACE:
            if self.do_reset:
                self.reset()
            self.cycle_run()

        elif key == arcade.key.RIGHT:
            self.speed = min(self.speed + 0.05, 1)
        elif key == arcade.key.LEFT:
            self.speed = max(self.speed - 0.05, 0.9)

    def cycle_run(self):
        self.stopped = not(self.stopped)

    def reset(self):
        self.do_reset = False
        self.agent.coord = np.array([0, 0])

    def end(self):
        import sys
        sys.exit()

    @staticmethod
    def boundary_threshold(pos):
        if pos[0] >= COLUMN_COUNT:
            pos[0] = COLUMN_COUNT-1
        elif pos[0] < 0:
            pos[0] = 0
        if pos[1] >= ROW_COUNT:
            pos[1] = ROW_COUNT-1
        elif pos[1] < 0:
            pos[1] = 0
        return pos

    def update(self, x):
        if not self.stopped:
            time.sleep(1-self.speed)
            self.step()

    def step(self, action=None):
        for entity in self.entities:
            if isinstance(entity, Agent):
                choice = random.randint(4)
                cur_pos = entity.coord
                new_pos = cur_pos + ACTION_PROFILE[choice]
                new_pos = Gridworld.boundary_threshold(new_pos)
                entity.coord = new_pos

                for other in self.entities:
                    if other is entity:
                        continue
                    if np.array_equal(new_pos, other.coord):
                        if other.is_terminal:
                            self.stopped = True
                            self.do_reset = True



class Entity:
    def __init__(self, x, y, cost, color):
        coord = np.array([x, y])
        self.coord = coord
        self.cost = cost
        self.color = color
        self.scale = 1

    def set_coord(self, coord):
        self.coord = coord

    def set_color(self, color):
        self.color = color


class Agent(Entity):
    def __init__(self, x, y, cost=None, color=arcade.color.AZURE):
        super(Agent, self).__init__(x, y, cost, color)
        # self.scale = 1.25

class Reward(Entity):
    def __init__(self, x, y, cost=0, color=arcade.color.GREEN):
        super(Reward, self).__init__(x, y, cost, color)
        self.is_terminal = True
        # self.scale = 2

class Wall(Entity):
    def __init__(self, x, y, end_coord, cost, color=arcade.color.BROWN):
        super(Wall, self).__init__(x, y, cost, color)




# class Env:
#     def __init__(self):
#         self.window = MainWindow()
#         self.game = Game()
#         self.game.init()

#     def main(self):
#         arcade.run()

#     def get_screen_pos_args(self, pos):
#         """
#         :param (numpy.ndarray, numpy.ndarray) pos: ((x1,y1), (x2,y2))
#         :return: center_x, center_y, width, height
#         :rtype: dict[str,int]
#         """
#         p1, p2 = pos
#         center = (p1 + p2) // 2
#         size = p2 - p1
#         return {
#             "center_x": center[0],
#             "center_y": self.window.height - center[1],
#             "width": size[0],
#             "height": size[1]}


# class MainWindow(arcade.Window):
#     """ Main application class. """

#     KeyRepeatDelayTime = 0.2
#     KeyRepeatTime = 0.05
#     KeyRepeatIgnoreKeys = (arcade.key.RETURN,)  # can lead to unexpected behavior

#     def __init__(self):
#         self.entity_pixel_size = 30
#         width = self.entity_pixel_size * (game.ROOM_WIDTH + 1 + game.KNAPSACK_WIDTH)
#         height = self.entity_pixel_size * (game.ROOM_HEIGHT + 1)
#         super(MainWindow, self).__init__(
#             width=width, height=height, title="PyOverheadGame!")
#         self.key_downs = {}  # key int idx -> delta time
#         self.set_icon(pyglet.image.load("%s/robot.png" % GFX_DIR))

#     def on_draw(self):
#         """
#         Called every frame for drawing.
#         """
#         arcade.start_render()
#         arcade.set_background_color(arcade.color.BABY_BLUE)
#         app.env.draw()

#     # Does not work?
#     # def on_resize(self, width, height):
#     #    #app.game.on_screen_resize()
#     #    pass

#     def update(self, delta_time):
#         """
#         Movement and game logic. This is called for every frame.

#         :param float delta_time: how much time passed
#         """
#         app.game.update(delta_time=delta_time)
#         for key, t in sorted(self.key_downs.items()):
#             t += delta_time
#             while t > self.KeyRepeatDelayTime:
#                 t -= self.KeyRepeatTime
#                 self.on_key_press(key=key, modifiers=0)
#             self.key_downs[key] = t

#     def on_key_press(self, key, modifiers):
#         """
#         Called whenever a key is pressed.
#         """
#         if key == arcade.key.UP:
#             app.game.on_key_arrow((0, -1))
#         elif key == arcade.key.DOWN:
#             app.game.on_key_arrow((0, 1))
#         elif key == arcade.key.LEFT:
#             app.game.on_key_arrow((-1, 0))
#         elif key == arcade.key.RIGHT:
#             app.game.on_key_arrow((1, 0))
#         elif key in (arcade.key.TAB, arcade.key.SPACE):
#             app.game.on_key_tab()
#         elif key == arcade.key.RETURN:
#             app.game.on_key_return()
#         elif key == arcade.key.ESCAPE:
#             app.game.on_key_escape()
#         if key not in self.KeyRepeatIgnoreKeys:
#             self.key_downs.setdefault(key, 0.0)

#     def on_key_release(self, key, modifiers):
#         """
#         Called when the user releases a key.
#         """
#         self.key_downs.pop(key, None)

#     def on_text(self, text):
#         app.game.on_text(text)

#     def on_text_motion(self, motion):
#         app.game.on_text_motion(motion)

#     def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
#         app.game.on_mouse_motion(x, self.height - y)

#     def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
#         app.game.on_mouse_press(x, self.height - y, button)

def main():
    Gridworld(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()

if __name__ == "__main__":
    main()

