from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.properties import ListProperty

Builder.load_string("""
<CustomButton>:
    size_hint: 1, None
    height: dp(150)
""")

class CustomButton(Button):
    # bg_color = ListProperty([1, 1, 1, 1])  # Initial color (white, fully opaque)
    #
    # def on_press(self):
    #     # Change to a semi-transparent red to check if it triggers
    #     self.bg_color = [1, 0, 0, 0.1]
    #
    # def on_release(self):
    #     # Reset to fully opaque white
    #     self.bg_color = [1, 1, 1, 1]
    pass
