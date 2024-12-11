from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
import random
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from kivy.utils import rgba
from plyer import accelerometer
from kivy.clock import mainthread

#Loading layout
Builder.load_string("""
<FlappyBirdGame>:
    name: "bird"
    canvas.before:
        Color:
            rgba: 0,0,0,1
        Rectangle:
            pos: self.pos
            size: self.size
""")

#Gravity and fly move
GRAVITY = 0.15
UP_MOVE = -5
FPS = 1/60

class Highscore(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open(r'flappy_bird.txt') as file:
            self.highscore = int(file.read())
        self.text = f"Highscore: {self.highscore}"
        self.color = rgba("FFFFFF")
        self.font_size = "35sp"
        self.pos_hint = {"center_x": 0.5, "bottom": 0.9}
        self.size_hint = (None, None)
        self.font_name = "jersey25-Regular.ttf"

class Score(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.text = f"Score: {self.score}"
        self.color = rgba("FFFFFF")
        self.font_size = "35sp"
        self.pos_hint = {"center_x": 0.5, "top": 0.99}
        self.size_hint = (None, None)
        self.font_name = "jersey25-Regular.ttf"


class Bird(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b_width = 50
        self.b_height = 30
        self.x = 175
        self.y = Window.height / 2 - self.b_height / 2
        self.dy = 0 # dy - starting vertical speed
        self.bird_img = Image(
            source='bird.png',
            size=(self.b_width, self.b_height),
            pos=(self.x, self.y)
        )
        self.bird_imgs = ['bird.png', 'bird_up.png']
        self.add_widget(self.bird_img)

    def flap(self):
        self.bird_img.source = self.bird_imgs[1]

    def move(self):
        self.y -= self.dy
        self.bird_img.pos = (self.x, self.y)

    def reset_position(self):
        self.x = 175
        self.y = Window.height / 2 - (self.b_height / 2)
        self.dy = 0
        self.bird_img.pos = (self.x, self.y)

class Obstacle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Images of pipes
        pipe_up_img = CoreImage("pipe_u.png")
        pipe_down_img = CoreImage("pipe_down.png")

        pipe_up_texture = pipe_up_img.texture
        pipe_down_texture = pipe_down_img.texture


        #Coordinates and values of positioning pipes
        #Random gap placement
        self.r_gap_pos = random.randint(-200, 200)
        # Pipe gap
        self.pipe_gap = 150

        #Width of pipe
        self.p_width = 100
        self.p_height = int(Window.height/2)
        self.up_pipe_h = self.p_height + abs(self.r_gap_pos)

        #X value of all pipes
        self.x = Window.width

        #Y values of pipes
        self.y_top = Window.height - self.p_height + (self.pipe_gap/2) + self.r_gap_pos
        if self.r_gap_pos >= 0:
            self.bottom_pipe_h = self.p_height + (2 * (self.r_gap_pos))
            self.y_bottom = 0 - (self.pipe_gap / 2) - self.r_gap_pos
        elif self.r_gap_pos < 0:
            self.bottom_pipe_h = self.p_height + abs(self.r_gap_pos)
            self.y_bottom = 0 - (self.pipe_gap / 2) + (2 * self.r_gap_pos)


        #Speed of pipes
        self.dx = -2

        #Adding pipes as rectangles
        with self.canvas.before:
            Color(1, 1, 1, 1)

            self.pipe_up = Rectangle(pos=(self.x, self.y_top),
                                     size=(self.p_width, self.up_pipe_h),
                                     texture=pipe_up_texture)

            self.pipe_down = Rectangle(pos=(self.x, self.y_bottom),
                                       size=(self.p_width, self.bottom_pipe_h),
                                       texture=pipe_down_texture)

        #Rectangles width and height
        self.pipe_up_width, self.pipe_up_height = self.pipe_up.size
        self.pipe_down_width, self.pipe_down_height = self.pipe_down.size

        #Adding pipe as img
        # self.pipe_up_img = Image(source="flappy_bird_imgs/pipe_u.png",
        #                          size_hint=(None, None),
        #                          size=(self.p_width, self.up_pipe_h),
        #                          pos= (self.x, self.y_top))
        # self.pipe_down_img = Image(source="flappy_bird_imgs/pipe_down.png",
        #                            size_hint = (None, None),
        #                            size=(self.p_width, self.bottom_pipe_h),
        #                            pos = (self.x, self.y_bottom))

        #Images
        # self.add_widget(self.pipe_up_img)
        # self.add_widget(self.pipe_down_img)

        #Rectangles
        # self.add_widget(self.pipe_up)
        # self.add_widget(self.pipe_down)

    #Move of pipes
    def move(self):
        self.x += self.dx
        #Images
        # self.pipe_up_img.pos = (self.x, self.y_top)
        # self.pipe_down_img.pos = (self.x, self.y_bottom)

        #Rectangles
        self.pipe_up.pos = (self.x, self.y_top)
        self.pipe_down.pos = (self.x, self.y_bottom)


class FlappyBirdGame(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Add background
        self.background = Image(source="bird_background.png",
                                allow_stretch = True,
                                keep_ratio = False)
        self.background.size = (Window.width, Window.height)
        self.background.pos = (0, 0)
        self.add_widget(self.background)

        # Adding bird
        self.bird = Bird()
        self.add_widget(self.bird)

        # Adding Obstacles
        self.obstacles = []

        #Adding Highscore
        self.highscore = Highscore()
        self.add_widget(self.highscore)

        #Adding Score
        self.score = Score()
        self.add_widget(self.score)

        #Binding keys on keyboard
        # Window.bind(on_key_down = self.on_key_down)

        #Initialize accelerometer
        try:
            accelerometer.enable()
            self.accelerometer_enabled = True
        except NotImplementedError:
            self.accelerometer_enabled = False
            print("Accelerometer not supported on this device")

        #Updating game with clock
        Clock.schedule_interval(self.update, FPS)

        #Starting game
        self.game_started = False
        # self.key_pressed = False
        self.reset_event = None
        self.pipe_event = None

        #Adding play again button
        self.p_again_btn = Button(
            background_normal="bird_again_btn.png",
            size_hint=(None, None),
            size=(50, 50)
        )
        self.p_again_btn.pos_hint = {"center_x": 0.4, "center_y": 0.4}
        self.p_again_btn.bind(on_press=self.game_start)
        self.add_widget(self.p_again_btn)

        #Adding go back button
        self.back_button = Button(
            background_normal='bird_back_btn.png',
            size_hint=(None, None),
            size=(50, 50)
        )
        self.back_button.pos_hint = {"center_x": 0.6, "center_y": 0.4}
        self.back_button.bind(on_press=self.switch_back_to_main)

    def switch_back_to_main(self, instance):
        self.manager.current = "Main Screen"
    def game_start(self, *args):
        if not self.game_started:
            self.game_started = True
            # Generating pipe every 1.5 second
            self.pipe_event = Clock.schedule_interval(self.generate_pipe, 1.8)
            self.remove_widget(self.p_again_btn)
            self.remove_widget(self.back_button)

    @mainthread
    def update(self, dt):
        if self.game_started:
            if self.accelerometer_enabled:
                self.handle_accelerometer()
            # Updating gravity
            self.bird.dy += GRAVITY
            self.bird.move()

            # Moving obstacles
            for obstacle in self.obstacles:
                obstacle.move()
                # Remove obstacle from screen
                if obstacle.x < -obstacle.p_width:
                    self.remove_widget(obstacle)
                    self.obstacles.remove(obstacle)

                self.check_collision(obstacle)
                self.score_up(obstacle)
                self.check_top_bottom()

    def handle_accelerometer(self):
        try:
            _, y, _ = accelerometer.acceleration
            if y > 0.2:
                self.bird.flap()
                if self.reset_event:
                    self.reset_event.cancel()

                self.reset_event = Clock.schedule_once(self.reset_bird_img, 0.5)
                self.bird.dy = UP_MOVE
            elif y < -0.2:
                self.bird.dy += GRAVITY
        except TypeError:
            pass

    # def on_key_down(self, window, key, *args):
    #     if key == 114:
    #         self.restart_game()
    #     elif key == 115:
    #         if not self.game_started:
    #             self.game_started = True
    #             # Generating pipe every 1.5 second
    #             self.pipe_event = Clock.schedule_interval(self.generate_pipe, 1.8)
    #     elif key == 273 and self.game_started:
    #         self.bird.flap()
    #         if self.reset_event:
    #             self.reset_event.cancel()
    #
    #         self.reset_event = Clock.schedule_once(self.reset_bird_img, 0.5)
    #         self.bird.dy = UP_MOVE

    def reset_bird_img(self, dt):
        self.bird.bird_img.source = self.bird.bird_imgs[0]

    def score_up(self, obstacle):
        bird_left = self.bird.x
        pipe_right = obstacle.x + obstacle.pipe_up_width
        if bird_left == pipe_right + 1:
            self.score.score += 1
            self.score.text = f"Score: {self.score.score}"

    def generate_pipe(self, dt):
        # Generate obstacles
        obstacle = Obstacle()
        self.add_widget(obstacle)
        self.obstacles.append(obstacle)
        self.remove_widget(self.highscore)
        self.remove_widget(self.score)
        self.add_widget(self.highscore)
        self.add_widget(self.score)


    # def check_collision(self):
    #     for obstacle in self.obstacles:
    #         bird_collision_box = Widget(size=(self.bird.b_width * 0.1, self.bird.b_height * 0.1),
    #                                     pos =(self.bird.x + self.bird.b_width * 0.35 ,
    #                                           self.bird.y + self.bird.b_height * 0.35))
    #
    #         if (bird_collision_box.collide_widget(obstacle.pipe_down_img) or
    #                 bird_collision_box.collide_widget(obstacle.pipe_up_img)):
    #             self.restart_game()


    # def check_collision(self, obstacle):
    #     if (self.bird.x < obstacle.pipe_up_img.x + obstacle.pipe_up_img.width and self.bird.x +
    #             self.bird.b_width > obstacle.pipe_up_img.x and
    #             self.bird.y < obstacle.pipe_up_img.y_top + obstacle.pipe_up_img.up_pipe_h and
    #             self.bird.y + self.bird.b_height > obstacle.pipe_up_img.y_top):
    #         self.restart_game()
    #
    #     if (self.bird.x < obstacle.pipe_down_img.x + obstacle.pipe_down_img.width and
    #         self.bird.x + self.bird.b_width > obstacle.pipe_down_img.x and
    #         self.bird.y < obstacle.pipe_down_img.y_bottom + obstacle.pipe_down_img.bottom_pipe_h and
    #         self.bird.y + self.bird.b_height > obstacle.pipe_down_img.y_bottom):
    #         self.restart_game()

    # def check_collision(self, obstacle):
    #     if (self.bird.x < obstacle.x + obstacle.width and self.bird.x +
    #             self.bird.b_width > obstacle.x and
    #             self.bird.y < obstacle.y_top + obstacle.up_pipe_h and
    #             self.bird.y + self.bird.b_height > obstacle.y_top):
    #         return True
    #
    #     if (self.bird.x < obstacle.x + obstacle.width and
    #         self.bird.x + self.bird.b_width > obstacle.x and
    #         self.bird.y < obstacle.y_bottom + obstacle.bottom_pipe_h and
    #         self.bird.y + self.bird.b_height > obstacle.y_bottom):
    #         return True
    #     return False

    # def check_collision(self, obstacle):
    #     between_pipes = (self.bird.x + self.bird.b_width > obstacle.x and
    #                      self.bird.x < obstacle.x + obstacle.pipe_up_width and
    #                      self.bird.y > obstacle.y_bottom + obstacle.pipe_down_height and
    #                      self.bird.y + self.bird.b_height < obstacle.y_top)
    #
    #     if self.bird.x + self.bird.b_width > obstacle.x:
    #         if not between_pipes:
    #             self.restart_game()

    def check_top_bottom(self):
        if self.bird.y + self.bird.b_height > Window.height:
            self.restart_game()
        elif self.bird.y < 0:
            self.restart_game()
    def check_collision(self, obstacle):
        # Define bird edges
        bird_top = self.bird.y + self.bird.b_height
        bird_bottom = self.bird.y
        bird_left = self.bird.x
        bird_right = self.bird.x + self.bird.b_width

        # Define pipe edges
        pipe_left = obstacle.x
        pipe_right = obstacle.x + obstacle.pipe_up_width
        pipe_top = obstacle.y_top
        pipe_bottom = obstacle.y_bottom + obstacle.pipe_down_height

        # Check if the bird is horizontally within the pipe's boundaries
        if bird_right > pipe_left and bird_left < pipe_right:
            # Check if the bird is outside the gap (collision occurs)
            if bird_top > pipe_top or bird_bottom < pipe_bottom:
                self.restart_game()

    def restart_game(self):
        self.add_widget(self.p_again_btn)
        self.add_widget(self.back_button)
        if self.score.score > self.highscore.highscore:
            self.highscore.highscore = self.score.score
            with open(r'flappy_bird.txt', mode='w') as file:
                file.write(str(self.highscore.highscore))
            self.highscore.text = f"Highscore: {self.highscore.highscore}"
        self.bird.reset_position()
        self.score.score = 0
        self.score.text = f"Score: {self.score.score}"
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        self.obstacles.clear()

        if self.pipe_event:
            self.pipe_event.cancel()
            self.pipe_event = None

        self.game_started = False

    def on_stop(self):
        if self.accelerometer_enabled:
            accelerometer.disabled()