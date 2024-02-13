import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image

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

    def __init__(self):
        super(SnakeGame, self).__init__()    
        self.sound = SoundLoader.load('background.mp3')
        self.sound.play()
        with self.canvas:
            self.background = Image(source='background.png', pos=self.pos, size=(900,600))


if __name__== '__main__':
    SnakePlusPlusApp().run()
