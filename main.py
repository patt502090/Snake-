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
from kivy.vector import Vector
from kivy.config import Config

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen


Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '600')

PLAYER_SIZE = 15

class StartScreen(Screen):
    pass 

class SnakeHead(Widget):
    orientation = (PLAYER_SIZE, 0)

    def reset_pos(self):
        """
        รีเซ็ตตำแหน่งของหัวงูไปที่กลางของหน้าต่าง. หรือ วางตำแหน่งผู้เล่นไว้ตรงกลางกระดานเกม
        """
        self.pos = [
            int(Window.width / 2 - (Window.width / 2 % PLAYER_SIZE)),
            int(Window.height / 2 - (Window.height / 2 % PLAYER_SIZE))
        ]
        self.orientation = (PLAYER_SIZE, 0)

    def move(self):
        """
        เลื่อนหัวงูไปในทิศทางที่ระบุโดย 'orientation'.
        """
        self.pos = Vector(*self.orientation) + self.pos
        
class Fruit(Widget):
    def move(self, new_pos):
        self.pos = new_pos

class SnakePlusPlusApp(App):
    def build(self):
        Window.size = (900, 600)
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(SnakeGame(name='game'))
        return sm




class SnakeGame(Screen):
    fruit = ObjectProperty(None)
    head = ObjectProperty(None)
    sound = None
    muted = False
    score = 0
    player_size = NumericProperty(PLAYER_SIZE)

    def __init__(self, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)
        self.sound = SoundLoader.load('background.mp3')
        self.sound.play()
        self.sound.volume = 0.5

        # Score box
        self.score_box = BoxLayout(orientation='horizontal', size_hint=(None, None), height=50)
        
        with self.score_box.canvas:
            Color(0, 0, 0)  # สีดำ
            self.score_background = Rectangle(pos=self.score_box.pos, size=self.score_box.size)

        self.score_label = Label(text=f'Score: {self.score}', size_hint=(None, None), height=50)
        self.score_box.add_widget(self.score_label)

        # Mute button
        self.mute_button = Button(text="Mute", size_hint=(None, None), size=(70, 50))
        self.mute_button.bind(on_press=self.toggle_sound)
        self.score_box.add_widget(self.mute_button)

        self.add_widget(self.score_box)

        self.mute_button.pos = (Window.width - self.mute_button.width, Window.height - self.mute_button.height)

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
        
        while not found:
            roll = [PLAYER_SIZE * randint(0, int(Window.width  / PLAYER_SIZE) - 1),
                    PLAYER_SIZE * randint(0, int(Window.height / PLAYER_SIZE) - 1)]

            found = True

        self.fruit.move(roll)


if __name__ == '__main__':
    SnakePlusPlusApp().run()