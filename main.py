import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window

class SnakePlusPlusApp(App):
    def build(self):
        Window.size = (900, 600)
        return Label(text='Hello, world!')
    
if __name__== '__main__':
    SnakePlusPlusApp().run()

   