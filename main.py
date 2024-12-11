import kivy
import plyer
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from main_screen import MainScreen
from snake import SnakeRunGame
from dino_game import DinoRunGame
from flappy_bird import FlappyBirdGame
from brick_breaker import BrickBreakerRun

# Ensure the window is resizable
# Window.resizable = True

# Enable borders for resizing with the mouse
# Window.borderless = False

Window.fullscreen = 'auto'

# Window.size = (480, 700)

class Interface(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_screen = MainScreen()
        snake = SnakeRunGame()
        dino = DinoRunGame()
        brick = BrickBreakerRun()
        bird = FlappyBirdGame()
        self.add_widget(main_screen)
        self.add_widget(snake)
        self.add_widget(dino)
        self.add_widget(brick)
        self.add_widget(bird)
class MobileApp(App):
    pass

MobileApp().run()