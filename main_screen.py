from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

Builder.load_string("""
#: import CustomButton custom_widgets
<MainScreen>:
    name: "Main Screen"
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(120)
            padding: [0,dp(10),0,dp(30)]
            Label:
                text: "Mobile App"
                font_size: "32sp"
                size_hint: 1, None
                color: 0,0,0,1
                height: dp(60)

        ScrollView:
            do_scroll_y: True
            BoxLayout:
                orientation: "vertical"
                padding: dp(16)
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
                CustomButton:
                    background_normal: "snake_img.png"
                    background_down: "snake_img_pressed.png"
                    on_press: root.switch_to_snake()

                CustomButton:
                    background_normal: "dino_img.png"
                    background_down: "dino_img_pressed.png"
                    on_press: root.switch_to_dino()

                CustomButton:
                    background_normal: "flappy_bird.png"
                    background_down: "flappy_bird_pressed.png"
                    on_press: root.switch_to_bird()
                CustomButton:
                    background_normal: "pac_man_img.png"
                    background_down: "pac_man_img_pressed.png"
                CustomButton:
                    background_normal: "bricks_img.png"
                    background_down: "bricks_img_pressed.png"
                    on_press: root.switch_to_brick()
""")

class MainScreen(Screen):
    def switch_to_bird(self):
        self.manager.current = "bird"
    def switch_to_snake(self):
        self.manager.current = "snake"
    def switch_to_dino(self):
        self.manager.current = "dino"
    def switch_to_brick(self):
        self.manager.current = "brick"
