import random
import time
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.utils import rgba
from kivy.graphics import Color, RoundedRectangle
from plyer import accelerometer
from kivy.clock import mainthread

# Constants
FPS = 1.0 / 60.0
GRAVITY = -1.2
JUMP_VELOCITY = 6
DINO_Y_POS = 16
GROUND_SPEED = 4
MIN_CACTUS_GAP = 200
MAX_CACTUS_GAP = 400
PTERA_SPEED = 5
PTERA_FLAP_INTERNAL = 0.2
DINO_MOVE_INTERNAL = 0.2
SCORE_GROW = 1.0 / 45.0

Builder.load_string("""
<DinoRunGame>:
    name: "dino"
    Ground:
        id: ground


<Ground>:
    size_hint: None, None
    size: (1202, 18)
    Image:
        id: image1
        source: "ground.png"
        size_hint: None, None
        size: (1202, 26)
        pos: (0, 0)
    Image:
        id: image2
        source: "ground.png"
        size_hint: None, None
        size: (1202, 26)
        pos: (1202, 0)

""")


class Score(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        with open("dino_data.txt") as dino_file:
            self.highscore = int(dino_file.read())
        self.text = f"Score: {self.score} Highscore: {self.highscore}"
        self.font_size = 21
        self.color = rgba("#6e5b57")
        self.size_hint = (None, None)
        self.pos_hint = {"right": 0.85, "top": 0.99}
        self.font_name = "jersey25-Regular.ttf"


class PTERA(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.altitudes = [95, 75, 45]
        self.size_hint = None, None
        self.size = (46, 40)
        self.pos = (random.randint(750, 1000), random.choice(self.altitudes))
        self.speed = PTERA_SPEED
        self.source = "ptera1.png"
        self.flap_images = ["ptera1.png", "ptera2.png"]
        self.flap_index = 0

        Clock.schedule_interval(self.flap, PTERA_FLAP_INTERNAL)

    def flap(self, dt):
        self.flap_index = (self.flap_index + 1) % len(self.flap_images)
        self.source = self.flap_images[self.flap_index]

    def update(self, dt):
        self.x -= PTERA_SPEED
        self.pos = (self.x, self.y)
        if self.x < -self.width:
            self.parent.remove_widget(self)


class Cactus(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cactus_type = random.choice(["cacti-small.png", "cacti-big.png"])
        self.source = cactus_type
        if cactus_type == "cacti-small.png":
            self.size = (45, 44)
        else:
            self.size = (65, 44)

        self.size_hint = None, None
        self.pos = (Window.width, DINO_Y_POS)
        self.speed = GROUND_SPEED

    def update(self, dt):
        self.x -= self.speed
        self.pos = (self.x, self.y)
        if self.x < -self.width:
            self.parent.remove_widget(self)


class Cloud(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "cloud.png"
        self.WIDTH, self.HEIGHT = 70, 40
        self.size_hint = None, None
        self.size = (self.WIDTH, self.HEIGHT)
        self.speed = 2
        self.reset()

    def reset(self):
        self.pos = (random.randint(Window.width + 100, Window.width + 200), random.randint(100, 200))

    def update(self, dt):
        self.x -= self.speed
        if self.x < - self.WIDTH:
            self.reset()
        self.pos = (self.x, self.y)


class Dino(Image):
    # Starting values
    g = GRAVITY  # -1.2
    up = JUMP_VELOCITY  # 6
    t = 0
    jumping = False
    crouching = False

    def __init__(self, owner, **kwargs):
        super().__init__(**kwargs)
        self.owner = owner
        self.source = "dino_1.png"
        self.size_hint = None, None
        self.size = (44, 48)
        self.pos = (20, DINO_Y_POS)
        self.dino_imgs = ["dino_1.png", "dino_2.png"]
        self.dino_move_index = 0
        self.dino_crouching_imgs = ["dino_ducking1.png", "dino_ducking2.png"]

        Clock.schedule_interval(self.dino_move, DINO_MOVE_INTERNAL)

    def dino_move(self, dt):
        if self.owner.game_over:
            self.source = "dino_.png"
        elif not self.crouching:
            self.dino_move_index = (self.dino_move_index + 1) % len(self.dino_imgs)
            self.source = self.dino_imgs[self.dino_move_index]
        else:
            self.dino_move_index = (self.dino_move_index + 1) % len(self.dino_crouching_imgs)
            self.source = self.dino_crouching_imgs[self.dino_move_index]

    def crouch(self):
        if not self.crouching:
            self.crouching = True
            self.pos = (self.x, DINO_Y_POS - 8)

    def stand(self):
        if self.crouching:
            self.crouching = False
            self.pos = (self.x, DINO_Y_POS)

    # Check if we are jumping
    def jump(self):
        if not self.jumping:
            self.up = JUMP_VELOCITY
            self.t = 0
            self.jumping = True

    # Animation of jumping
    def update(self, dt):
        if self.jumping:
            self.source = "dino_.png"
            self.up += self.g * self.t
            self.y += self.up
            self.t += dt

            if self.y <= DINO_Y_POS:
                self.t = 0
                self.y = DINO_Y_POS
                self.up = JUMP_VELOCITY
                self.jumping = False


class Ground(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ground_length = 1202

    def update(self, dt):
        self.ids.image1.x -= GROUND_SPEED
        self.ids.image2.x -= GROUND_SPEED

        if self.ids.image1.x + self.ground_length < 0:
            self.ids.image1.x = self.ids.image2.x + self.ground_length
        elif self.ids.image2.x + self.ground_length < 0:
            self.ids.image2.x = self.ids.image1.x + self.ground_length


class DinoRunGame(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dino = Dino(owner=self)
        self.ground = self.ids.ground
        self.score = Score()

        self.add_widget(self.dino)
        self.add_widget(self.score)

        self.obstacles = []
        self.obstacles_start = time.time()
        self.minimum_time = 1.5

        self.clouds = [Cloud() for _ in range(5)]
        for cloud in self.clouds:
            self.add_widget(cloud)

        self.game_over_image = Image(source="game_over.png")
        self.game_over_image.size_hint = None, None
        self.game_over_image.size = (200, 100)
        self.game_over_image.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.replay_button = Button(background_normal="replay_button.png")
        self.replay_button.size_hint = None, None
        self.replay_button.size = (50, 50)
        self.replay_button.pos_hint = {"center_x": 0.4, "center_y": 0.43}
        self.replay_button.bind(on_press=self.reset_game)

        self.back_button = Button(
            background_normal="back_btn.png",
            size_hint=(None, None),
            size=(50, 50)
        )
        self.back_button.pos_hint = {"center_x": 0.6, "center_y": 0.43}
        self.back_button.bind(on_press=self.switch_to_main)

        self.game_over = False

        #Initialize accelerometer
        try:
            accelerometer.enable()
            self.accelerometer_enabled = True
        except NotImplementedError:
            self.accelerometer_enabled = False
            print("Accelerometer not supported on this device")

        Clock.schedule_interval(self.update, FPS)
        Clock.schedule_interval(self.increment_score, SCORE_GROW)
        # Window.bind(on_key_down=self.on_key_down)
        # Window.bind(on_key_up=self.on_key_up)

    def switch_to_main(self, instance):
        self.manager.current = "Main Screen"

    def increment_score(self, dt):
        global GROUND_SPEED
        if not self.game_over:
            self.score.score += 1
            self.score.text = f"Score: {self.score.score} Highscore: {self.score.highscore}"

            if self.score.score % 500 == 0:
                GROUND_SPEED += 0.25

    def update(self, dt):
        if self.game_over:
            return

        #Accelerometer
        if self.accelerometer_enabled:
            self.handle_accelerometer()

        self.dino.update(dt)
        self.ground.update(dt)
        for cloud in self.clouds:
            cloud.update(dt)

        for obstacle in self.obstacles:
            obstacle.update(dt)

        if len(self.obstacles) < 2:
            self.spawn_obstacle()

        self.obstacles = [obstacle for obstacle in self.obstacles if obstacle.x > -obstacle.width]

        self.check_collisions()

    @mainthread
    def handle_accelerometer(self):
        try:
            x, y, _ = accelerometer.acceleration
            if y > 0.4:
                self.dino.jump()
            elif y < -0.4:
                self.dino.crouch()
            else:
                self.dino.stand()
        except TypeError:
            pass

    def on_stop(self):
        if self.accelerometer_enabled:
            accelerometer.disable()

    def spawn_obstacle(self):
        if random.random() < 0.8:
            self.spawn_cactus()
        else:
            self.spawn_ptera()

    def spawn_cactus(self):
        if self.obstacles:
            last_cactus = self.obstacles[-1]
            new_cactus_x = last_cactus.x + last_cactus.width + random.randint(MIN_CACTUS_GAP, MAX_CACTUS_GAP)
        else:
            new_cactus_x = Window.width + random.randint(MIN_CACTUS_GAP, MAX_CACTUS_GAP)

        new_cactus = Cactus()
        new_cactus.pos = (new_cactus_x, DINO_Y_POS)
        self.obstacles.append(new_cactus)
        self.add_widget(new_cactus)

    def spawn_ptera(self):
        new_ptera = PTERA()
        self.obstacles.append(new_ptera)
        self.add_widget(new_ptera)

    def check_collisions(self):
        for obstacle in self.obstacles:
            if self.dino.crouching:
                dino_collison_box = Widget(size=(self.dino.width * 0.7, self.dino.height * 0.5),
                                           pos=(self.dino.x + self.dino.width * 0.15, self.dino.y))
            else:
                dino_collison_box = Widget(
                    size=(self.dino.width * 0.7, self.dino.height * 0.7),
                    pos=(self.dino.x + self.dino.width * 0.15, self.dino.y + self.dino.height * 0.15)
                )
            if dino_collison_box.collide_widget(obstacle):
                self.end_game()

    def end_game(self):
        global GROUND_SPEED
        self.game_over = True
        if self.score.score > self.score.highscore:
            self.score.highscore = self.score.score
            with open("dino_data.txt", mode="w") as dino_file:
                dino_file.write(str(self.score.highscore))
        self.score.score = 0
        GROUND_SPEED = 4
        self.add_widget(self.game_over_image)
        self.add_widget(self.replay_button)
        self.add_widget(self.back_button)

    def reset_game(self, *args):
        self.game_over = False
        self.remove_widget(self.game_over_image)
        self.remove_widget(self.replay_button)
        self.remove_widget(self.back_button)
        self.dino.pos = (20, DINO_Y_POS)
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        self.obstacles = []

    # def on_key_down(self, window, key, *args):
    #     if key == 32:
    #         self.dino.jump()
    #
    #     if key == 274:
    #         if not self.game_over:
    #             self.dino.crouch()
    #
    # def on_key_up(self, window, key, *args):
    #     if key == 274:
    #         self.dino.stand()
