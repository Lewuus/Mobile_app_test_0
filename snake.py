from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from plyer import accelerometer
from kivy.clock import mainthread
import random
from kivy.utils import rgba



# SCREEN_WIDTH = Window.width
# SCREEN_HEIGHT = Window.height
FPS = 1.0/10.0

Builder.load_string("""
<SnakeRunGame>:
    name: "snake"
    canvas.before:
        Color:
            rgba: 0,0,0,1
        Rectangle:
            pos: self.pos
            size: self.size
""")

class Score(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        with open('snake_data.txt') as file:
            self.highscore = int(file.read())
        self.text = f"Score: {self.score} Highscore: {self.highscore}"
        self.font_size = "30sp"
        self.color = rgba("#FFFFFF")
        self.size_hint = (None, None)
        self.pos_hint = {"center_x": 0.5, "top": 0.99}
        self.font_name = "jersey25-Regular.ttf"

class SnakeRunGame(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Initialize accelerometer
        try:
            accelerometer.enable()
            self.accelerometer_enabled = True
        except NotImplementedError:
            print("Accelerometer not supported on this device.")
            self.accelerometer_enabled = False

        #Adding scoreboard
        self.score = Score()
        self.add_widget(self.score)

        #Starting game condition
        self.game_over = False

        #Starting game
        self.start_game()

        #Updating screen for smooth animation
        Clock.schedule_interval(self.update, FPS)

        # #Bind keyboard events
        # Window.bind(on_key_down = self.on_key_down)

    def start_game(self):
        # Add snake image
        self.snake = [Image(source='snake_body.png', pos=(100, 100), size_hint=(None, None), size=(20, 20))]
        self.add_widget(self.snake[0])

        # Add food image
        self.food = Image(source='food_img.png', pos=(300, 300), size_hint=(None, None), size=(10, 10))
        self.add_widget(self.food)

        # Starting move direction
        self.direction = 'right'

        #Spawn first food
        self.spawn_food()

        #Game over message
        self.game_over_label = Label(text="Game Over\nPress Spacebar to play again",
                                     halign = "center",
                                     valign = "middle",
                                     font_size="30sp",
                                     size_hint=(None, None),
                                     size = (Window.width - 20, 40),
                                     pos_hint={"center_x": 0.5, "center_y": 0.5},
                                     opacity= 0,
                                     font_name = "jersey25-Regular.ttf"
                                    )
        self.add_widget(self.game_over_label)

        #Play again Button
        self.play_again_btn = Button(
            background_normal = "play_again_btn.png",
            size_hint = (None, None),
            size = (50,50)
        )
        self.play_again_btn.pos_hint = {"center_x": 0.4, "center_y": 0.4}
        self.play_again_btn.bind(on_press = self.reset_game)

        #Go back button
        self.back_button = Button(
            background_normal = 'snake_back_btn.png',
            size_hint=(None, None),
            size=(50, 50)
        )
        self.back_button.pos_hint = {"center_x": 0.6, "center_y": 0.4}
        self.back_button.bind(on_press = self.switch_back_to_main)

    def switch_back_to_main(self, instance):
        self.manager.current = "Main Screen"
    # Setting keys on keyboards to the right directions and restarting game
    # def on_key_down(self, window, key, *args):
    #     #Movement
    #     if not self.game_over:
    #         if key == 273 and self.direction != 'down':
    #             self.direction = "up"
    #         elif key == 274 and self.direction != 'up':
    #             self.direction = "down"
    #         elif key == 275 and self.direction != 'left':
    #             self.direction = "right"
    #         elif key == 276 and self.direction != 'right':
    #             self.direction = "left"

    #Method responsible for updating movement on screen
    @mainthread
    def update(self, dt):
        if self.game_over:
            return

        #Read acclerometer and move by this
        if self.accelerometer_enabled:
            if not self.game_over:
                try:
                    x, y, _ = accelerometer.acceleration
                    if abs(x) > abs(y):
                        if x > 0.2 and self.direction != 'left':
                            self.direction = 'right'
                        elif x < -0.2 and self.direction != 'right':
                            self.direction = 'left'
                    else:
                        if y > 0.2 and self.direction != 'down':
                            self.direction = 'up'
                        elif y < -0.2 and self.direction != 'up':
                            self.direction = 'down'
                except TypeError:
                    # Accelerometer may return None during initial polling
                    pass

        #Movement logic
        x, y = self.snake[0].pos
        if self.direction == 'up':
            y += 20
        elif self.direction == 'down':
            y -= 20
        elif self.direction == 'right':
            x += 20
        elif self.direction == 'left':
            x -= 20

        #Cheking collisons with walls
        if x < 0 or x >= Window.width or y < 0 or y >= Window.height:
            self.end_game()

        #Checking collisons with itself
        for segment in self.snake[1:]:
            if self.snake[0].pos == segment.pos:
                self.end_game()
                return

        #Giving coordinates to the previous segment of snake
        prev_positions = [(segment.pos[0], segment.pos[1]) for segment in self.snake]

        #Giving actual coordinate to the head of snake
        self.snake[0].pos = (x, y)

        #Setting the position of previous segment of snake, to given coordinates
        for i in range(1, len(self.snake)):
            self.snake[i].pos = prev_positions[i-1]

        #Check for collison with food
        if self.check_collision(self.snake[0], self.food):
            self.grow_snake(prev_positions[-1])
            self.spawn_food()
            self.score.score += 1
            self.score.text = f"Score: {self.score.score} Highscore: {self.score.highscore}"


    def on_stop(self):
        if self.accelerometer_enabled:
            accelerometer.disable()

    #Method responsible for checking collision
    def check_collision(self, head, food):
        if head.collide_widget(food):
            return True
        else:
            return False

    #Method responsible for growth of snake
    def grow_snake(self, pos_new_seg):
        new_seg = Image(source='snake_body.png', size_hint=(None, None), size=(20, 20), pos = pos_new_seg)
        self.snake.append(new_seg)
        self.add_widget(new_seg)

    #Method responsible for spawning new food
    def spawn_food(self):
        food_x = random.randint(0, (Window.width - 20) // 20) * 20
        food_y = random.randint(0, (Window.height - 20) // 20) * 20
        self.food.pos = (food_x, food_y)

    #Method for ending game
    def end_game(self):
        #End Game Values
        self.game_over = True
        self.game_over_label.opacity = 1
        self.add_widget(self.play_again_btn)
        self.add_widget(self.back_button)
        if self.score.score > self.score.highscore:
            self.score.highscore = self.score.score
            with open('snake_data.txt', mode='w') as file:
                file.write(str(self.score.highscore))

        #Removing snake and food from the screen
        for segment in self.snake:
            self.remove_widget(segment)
        self.remove_widget(self.food)

    #Resetting game
    def reset_game(self, *args):
        #Resetting game values
        self.game_over = False
        self.game_over_label.opacity = 0
        self.remove_widget(self.play_again_btn)
        self.remove_widget(self.back_button)
        self.score.score = 0
        self.score.text = f"Score: {self.score.score} Highscore: {self.score.highscore}"

        #Starting Game Again
        self.start_game()
