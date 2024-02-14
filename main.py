import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button


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

    def __init__(self):
        super(SnakeGame, self).__init__()    
        self.sound = SoundLoader.load('background.mp3')
        self.sound.play()

        self.mute_button = Button(text="Mute", size_hint=(None, None), pos=(Window.width - 20, Window.height - 90))
        self.mute_button.bind(on_press=self.toggle_sound)
        self.add_widget(self.mute_button)
        

    def toggle_sound(self, instance):
        if self.sound:
            if not self.muted:
                self.sound.volume=0
                self.muted = True
                self.mute_button.text = "Unmute"
            else:
                self.sound.volume=1
                self.muted = False
                self.mute_button.text = "Mute"

    

if __name__== '__main__':
    SnakePlusPlusApp().run()
