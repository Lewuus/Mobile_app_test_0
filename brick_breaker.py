from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty
from kivy.utils import rgba
from plyer import accelerometer
from kivy.clock import mainthread


SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
FPS = 1.0/60.0

Builder.load_string("""
<BrickBreakerRun>:
    name: "brick"
    canvas.before:
        Color:
            rgba: 0,0,0,1
        Rectangle:
            pos: self.pos
            size: self.size
""")

#Class resposnsible for score
class Level(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 0
        self.text = f"Level: {self.level}"
        self.font_size = "30sp"
        self.color = rgba("#FFFFFF")
        self.size_hint = (None, None)
        self.pos_hint = {"bottom": 0.99, "right": 0.25}
        self.font_name = "jersey25-Regular.ttf"

#Class responsible for highest level
class Highest_level(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open(r'brick_breaker.txt') as file:
            self.highest_level = int(file.read())
        self.text = f"Highest Level: {self.highest_level}"
        self.font_size = "30sp"
        self.color = rgba("FFFFFF")
        self.size_hint = (None, None)
        self.pos_hint = {"bottom": 0.99, "right": 0.87}
        self.font_name = "jersey25-Regular.ttf"

#Class responsible for winning
class GameWin(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 5
        self.text = f"Win! You are going to the next level in {self.counter}"
        self.font_size = "30sp"
        self.color = rgba("FFFFFF")
        self.size_hint = (None, None)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.font_name = "jersey25-Regular.ttf"
        self.opacity = 0

#Class responsible for game over
class GameOver(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Values for game over widget
        self.text = "You lose!"
        self.font_size = "30sp"
        self.color = rgba("FFFFFF")
        self.size_hint = (None, None)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.font_name = "jersey25-Regular.ttf"
        self.opacity = 0


#Class responsible for displaying bricks
class Brick(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.BWIDTH = 50
        self.BHEIGHT = Window.height * 0.05 #43.75
        self.brick_list = []
        self.delete_brick_count = 0
        self.start_rows = 0.8


    #Method responsible for displaying bricks
    def initialize_bricks(self):
        min_bricks = 5  # Minimum number of bricks per row
        left_right_padding = 25  # Padding from the left and right walls
        max_brick_width = 50  # Max brick width

        # Calculate brick width dynamically
        available_width = Window.width - 2 * left_right_padding
        num_bricks = max(min_bricks,
                         available_width // (max_brick_width + 20))  # Adding 20 as an initial larger spacing
        brick_width = min(max_brick_width, available_width // num_bricks)

        # Calculate spacing between bricks
        spacing = (available_width - (brick_width * num_bricks)) / (num_bricks - 1) if num_bricks > 1 else 0

        self.BWIDTH = brick_width
        self.BHEIGHT = Window.height * 0.05


        # Generate rows and columns of bricks
        for row in range(int(self.start_rows * Window.height), int(Window.height - 49), 50):
            x_position = left_right_padding
            for _ in range(num_bricks):
                brick = Image(source="paddle.png", size=(self.BWIDTH, self.BHEIGHT))
                brick.pos = (x_position, row)
                self.brick_list.append(brick)
                self.add_widget(brick)
                x_position += brick_width + spacing  # Adjust by spacing

        self.no_of_bricks = len(self.brick_list)


#Class responsible for paddle
class Paddle(Widget):
    pad_x = NumericProperty(240)
    pad_y = NumericProperty(100)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.WIDTH = Window.width * 0.15
        self.HEIGHT = Window.height * 0.05
        self.pad_img = Image(source="brick.png", size=(self.WIDTH, self.HEIGHT))
        self.add_widget(self.pad_img)
        self.bind(pad_x=self.update_position, pad_y=self.update_position)
        self.update_position()

    def update_position(self, *args):
        self.pad_img.pos = (self.pad_x, self.pad_y)

#Class responsible for ball
class Ball(Widget):
    ball_x = NumericProperty(175)
    ball_y = NumericProperty(100)
    ball_vel_x = 2.5
    ball_vel_y = 2.5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Creating ball
        self.WIDTH = 15
        self.HEIGHT = 15
        self.ball_img = Image(source='my_ball.png', size=(self.WIDTH, self.HEIGHT))
        self.add_widget(self.ball_img)

        #Updating position of ball
        self.bind(ball_x = self.update_position, ball_y = self.update_position)
        self.update_position()

    #Method for updating position of ball
    def update_position(self, *args):
        self.ball_img.pos = (self.ball_x, self.ball_y)

    #Method responsible for moving ball
    def moveBall(self):
        self.ball_x += self.ball_vel_x
        self.ball_y += self.ball_vel_y

#Class responsible for running game
class BrickBreakerRun(Screen):
    game_over_flag = BooleanProperty(False)
    game_win_flag = BooleanProperty(False)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Add Level to the game
        self.level = Level()
        self.add_widget(self.level)

        #Add Highest level to the game
        self.highest_level = Highest_level()
        self.add_widget(self.highest_level)

        #Add ball to the window
        self.ball = Ball()
        self.add_widget(self.ball)

        #Add paddle to the window
        self.pad = Paddle()
        self.add_widget(self.pad)

        #Add bricks to the window
        self.brick = Brick()
        self.add_widget(self.brick)
        self.brick.initialize_bricks()

        #Add game_over logic
        self.game_over = GameOver()
        self.add_widget(self.game_over)

        #Add win game logic
        self.game_win = GameWin()
        self.add_widget(self.game_win)

        #Initialize accelerometer
        try:
            accelerometer.enable()
            self.accelerometer_enabled = True
        except NotImplementedError:
            self.accelerometer_enabled = False
            print("Accelerometer not supported on this device")

        #Bining keys
        # Window.bind(on_key_down = self.on_key_down)

        #Calling update method
        Clock.schedule_interval(self.update, FPS)

        #Play again button
        self.play_again_btn = Button(
            background_normal = "brick_again_btn.png",
            size_hint = (None, None),
            size = (50, 50)
        )
        self.play_again_btn.pos_hint = {"center_x": 0.4, "center_y": 0.4}
        self.play_again_btn.bind(on_press=self.reset_game)
        #Back Button
        self.back_button = Button(
            background_normal = "brick_back_btn.png",
            size_hint = (None, None),
            size=(50, 50)
        )
        self.back_button.pos_hint = {"center_x": 0.6, "center_y": 0.4}
        self.back_button.bind(on_press=self.switch_back_to_main)



    #Switch back to main method
    def switch_back_to_main(self, instance):
        self.manager.current = "Main Screen"

    def reset_game(self, *args):
        #Resetting ball to starting position
        self.ball.ball_x = 175
        self.ball.ball_y = 100
        self.ball.update_position()

        # Reset paddle position
        self.pad.pad_x = 240
        self.pad.pad_y = 100
        self.pad.update_position()

        # Clear bricks
        if self.game_win_flag and self.brick.start_rows > 0.2:
            self.brick.start_rows -= 0.1
            self.ball.ball_vel_x *= 1.2
            self.ball.ball_vel_y *= 1.2
        else:
            self.brick.start_rows = 0.8
            self.ball.ball_vel_x = 2.5
            self.ball.ball_vel_y = 2.5
            self.level.level = 0

        # Resetting labels of level and highest level
        self.level.text = f"Level: {self.level.level}"
        self.highest_level.text = f"Highest Level: {self.highest_level.highest_level}"

        #Resetting counter
        self.game_win.counter = 5

        for brick in self.brick.brick_list:
            brick.pos = (1000, 1000)
            self.remove_widget(brick)
        self.brick.brick_list.clear()
        self.bricks_to_remove.clear()

        #Initialize bricks again
        self.brick.initialize_bricks()

        #Resetting game variables
        self.game_over_flag = False
        self.remove_widget(self.back_button)
        self.remove_widget(self.play_again_btn)
        self.game_over.opacity = 0
        self.game_win.opacity = 0

    #Method responsible for pad movement
    # def on_key_down(self, window, key, *args):
    #     #Left key
    #     if key == 276:
    #         self.pad.pad_x -= 40
    #     #Right key
    #     elif key == 275:
    #         self.pad.pad_x += 40

    #Method responsible for updating whole game
    @mainthread
    def update(self, dt):
        if self.game_over_flag:
            return

        if self.accelerometer_enabled:
            self.handle_accelerometer()

        #Ball moving
        self.ball.moveBall()

        #Check for collision with walls
        if self.ball.ball_x < 0 or self.ball.ball_x > Window.width - self.ball.WIDTH:
            self.ball.ball_vel_x = -self.ball.ball_vel_x

        if self.ball.ball_y > Window.height - self.ball.HEIGHT:
            self.ball.ball_vel_y = -self.ball.ball_vel_y

        #Check for game lose
        if self.ball.ball_y < 0:
            self.end_game()

        #Check for collisons with paddle
        if self.check_collision(self.ball.ball_img, self.pad.pad_img):
            self.ball.ball_vel_y = -self.ball.ball_vel_y

        #Check if pad is not crossing walls
        if self.pad.pad_x < 0:
            self.pad.pad_x = 0
        elif self.pad.pad_x > Window.width - self.pad.WIDTH:
            self.pad.pad_x = Window.width - self.pad.WIDTH

        #Check for collisions with bricks
        self.bricks_to_remove = []
        for brick in self.brick.brick_list:
            if self.check_collision(self.ball.ball_img, brick):
                self.ball.ball_vel_y = -self.ball.ball_vel_y
                brick.pos = (1000, 1000)
                self.bricks_to_remove.append(brick)
                self.brick.no_of_bricks -= 1

        for brick in self.bricks_to_remove:
            self.remove_widget(brick)
            self.brick.brick_list.remove(brick)

        if self.brick.no_of_bricks == 0:
            Clock.unschedule(self.update)
            self.win_game()

    #Accelerometer
    def handle_accelerometer(self):
        try:
            x, _, _ = accelerometer.acceleration
            if x:
                self.pad.pad_x += x * 10
        except TypeError:
            pass

    def on_stop(self):
        if self.accelerometer_enabled:
            accelerometer.disable()

    #Condition check for paddle with ball
    def check_collision(self, widget1, widget2):
        return (
            widget1.x < widget2.right and
            widget1.right > widget2.x and
            widget1.y < widget2.top and
            widget1.top > widget2.y
        )

    def end_game(self):
        self.game_over_flag = True
        self.game_win_flag = False
        self.ball.ball_vel_x = 0
        self.ball.ball_vel_y = 0
        self.game_over.opacity = 1
        self.add_widget(self.back_button)
        self.add_widget(self.play_again_btn)
        if self.level.level > self.highest_level.highest_level:
            self.highest_level.highest_level = self.level.level
            with open(r'brick_breaker.txt', mode='w') as file:
                file.write(str(self.highest_level.highest_level))

    def win_game(self):
        self.current_b_vel_x = self.ball.ball_vel_x
        self.current_b_vel_y = self.ball.ball_vel_y
        self.ball.ball_vel_x = 0
        self.ball.ball_vel_y = 0
        self.game_win.opacity = 1
        self.game_win.counter = 5
        self.game_win.text = f"Win! You are going to the next level in {self.game_win.counter}"
        Clock.schedule_interval(self.counter_down, 1)

        #Increment level
        self.level.level += 1
        self.level.text = f"Level: {self.level.level}"

    def counter_down(self, dt):
        if self.game_win.counter > 1:
            self.game_win.counter -= 1
            self.game_win.text = f"Win! You are going to the next level in {self.game_win.counter}"
        else:
            # Stop the counters and reset the game
            Clock.unschedule(self.counter_down)
            self.game_win_flag = True
            self.ball.ball_vel_y = self.current_b_vel_y
            self.ball.ball_vel_x = self.current_b_vel_x
            self.reset_game()
            self.game_win_flag = False
            Clock.schedule_interval(self.update, FPS)






