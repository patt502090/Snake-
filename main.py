import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty
from random import randint

PLAYER_SIZE = 40
class SnakeHead(Widget):
    def move(self, new_pos):
        self.pos = new_pos

class Fruit(Widget):
    def move(self, new_pos):
        self.pos = new_pos

class SnakePlusPlusApp(App):
    def build(self):
        Window.size = (900, 600)
        game = SnakeGame()
        return game

class SnakeGame(Widget):
    fruit = ObjectProperty(None)
    head = ObjectProperty(None)
    sound = None
    muted = False
    score = 0
    player_size = NumericProperty(PLAYER_SIZE)

    def __init__(self):
        super(SnakeGame, self).__init__()
        self.sound = SoundLoader.load('background.mp3')
        self.sound.play()
        self.sound.volume = 0.5
        """with self.canvas:
            self.background = Image(source='background.png', pos=self.pos, size=(900, 600))"""

        self.mute_button = Button(text="Mute", size_hint=(None, None), pos=(Window.width - 20, Window.height - 90))
        self.mute_button.bind(on_press=self.toggle_sound)
        self.add_widget(self.mute_button)

        self.score_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)

        with self.score_box.canvas:
            Color(0, 0, 0)  
            self.score_box_rect = Rectangle(pos=self.score_box.pos, size=self.score_box.size)

        self.score_label = Label(text=f'Score: {self.score}', size_hint=(None, None), height=50)
        self.score_box.add_widget(self.score_label)
        self.add_widget(self.score_box)
        self.spawn_fruit()

    def toggle_sound(self, instance):
        if self.sound:
            if not self.muted:
                self.sound.volume = 0
                self.muted = True
                self.mute_button.text = "Unmute"
            else:
                self.sound.volume = 0.5
                self.muted = False
                self.mute_button.text = "Mute"

    def spawn_fruit(self):

        roll = self.fruit.pos
        found = False
        print(Window.width)
        while not found:

            

            roll = [PLAYER_SIZE *
                    randint(0, int(Window.width  / PLAYER_SIZE) - 1),
                    PLAYER_SIZE *
                    randint(0, int(Window.height / PLAYER_SIZE) - 1)]

            found = True

        self.fruit.move(roll)

if __name__ == '__main__':
    SnakePlusPlusApp().run()
