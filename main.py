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
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '600')

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 900

PLAYER_SIZE = 50
SPEED = 0.1

class StartScreen(Screen):
    def start_game(self):
        self.manager.current = "game"
        self.manager.get_screen('game').start_game_sound()
        

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

class SnakeTail(Widget):

    def move(self, new_pos):
        self.pos = new_pos

class smartGrid:

    def __init__(self):

        self.grid = [[False for i in range(WINDOW_HEIGHT)]
                    for j in range(WINDOW_WIDTH)]

    def __getitem__(self, coords):
        return self.grid[coords[0]][coords[1]]

    def __setitem__(self, coords, value):
        self.grid[coords[0]][coords[1]] = value

class SnakeGame(Screen):
    fruit = ObjectProperty(None)
    head = ObjectProperty(None)
    sound = None
    muted = False
    score = NumericProperty(0)
    player_size = NumericProperty(PLAYER_SIZE)
    ck = False

    def __init__(self, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        print(self.size,"ff")
        Window.bind(on_key_down=self.key_action)
        
        if PLAYER_SIZE < 3:
            raise ValueError("ขนาดโปรแกรมเล่นควรมีอย่างน้อย 3 px")

        if WINDOW_HEIGHT < 3 * PLAYER_SIZE or WINDOW_WIDTH < 3 * PLAYER_SIZE:
            raise ValueError(
                "ขนาดหน้าต่างต้องมีขนาดใหญ่กว่าขนาดเครื่องเล่นอย่างน้อย 3 เท่า")

        self.timer = Clock.schedule_interval(self.refresh, SPEED)
        self.tail = []
        self.restart_game()
        
        
    def refresh(self, dt):
        if not (0 <= self.head.pos[0] < WINDOW_WIDTH) or not (0 <= self.head.pos[1] < WINDOW_HEIGHT):
            self.ck = True
            self.restart_game()
            return
        
        if self.occupied[self.head.pos] is True:
            self.ck = True
            self.restart_game()
            return
        
        #เคลื่อนที่หางงู
        self.occupied[self.tail[-1].pos] = False
        self.tail[-1].move(self.tail[-2].pos)
        
        for i in range(2, len(self.tail)):
            self.tail[-i].move(new_pos=(self.tail[-(i + 1)].pos))

        self.tail[0].move(new_pos=self.head.pos)
        self.occupied[self.tail[0].pos] = True
        
        self.head.move()
        
        # ตรวจสอบว่าเราพบผลไม้หรือไม่ หากพบ ให้เพิ่มอีกหาง
        if self.head.pos == self.fruit.pos:
            self.score += 1
            self.score_label.text = f'Score: {self.score}' 
            self.tail.append(
                SnakeTail(
                    pos=self.head.pos,
                    size=self.head.size))
            self.add_widget(self.tail[-1])
            self.spawn_fruit()

        
    def play_button_click_sound(self):
        button_click_sound = SoundLoader.load('clickbuttonV2.wav')
        if button_click_sound:
            button_click_sound.play()

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


        self.tail = []
        self.restart_game()

    def start_game_sound(self):

        
        if self.ck:
            self.sound.stop()
        self.sound = SoundLoader.load('background.mp3')
        self.sound.play()        
        if not self.muted:
            self.sound.volume = 0.5
        else:
            self.sound.volume = 0

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
            roll = [PLAYER_SIZE *
                    randint(0, int(WINDOW_WIDTH / PLAYER_SIZE) - 1),
                    PLAYER_SIZE *
                    randint(0, int(WINDOW_HEIGHT / PLAYER_SIZE) - 1)]
            if self.occupied[roll] is True or roll == self.head.pos:
                continue
            found = True

        self.fruit.move(roll)


    def restart_game(self):
        if self.ck:
            print("check")
            self.start_game_sound()
        self.occupied = smartGrid()
        self.timer.cancel()
        self.timer = Clock.schedule_interval(self.refresh, SPEED)
        self.head.reset_pos()
        self.score = 0
        
        for block in self.tail:
            self.remove_widget(block)
            
        self.tail = []
        
        self.tail.append(
            SnakeTail(
                pos=(self.head.pos[0] - PLAYER_SIZE, self.head.pos[1]),
                size=(self.head.size)
            )
        )
        self.add_widget(self.tail[-1])
        self.occupied[self.tail[-1].pos] = True
        
        self.tail.append(
            SnakeTail(
                pos=(self.head.pos[0] - 2 * PLAYER_SIZE, self.head.pos[1]),
                size=(self.head.size)
            )
        )
        self.add_widget(self.tail[-1])
        self.occupied[self.tail[1].pos] = True

        self.spawn_fruit()
        
    def key_action(self, *args):
        command = list(args)[3]
        if command == 'w' or command == 'up':
            self.head.orientation = (0, PLAYER_SIZE)
        elif command == 's' or command == 'down':
            self.head.orientation = (0, -PLAYER_SIZE)
        elif command == 'a' or command == 'left':
            self.head.orientation = (-PLAYER_SIZE, 0)
        elif command == 'd' or command == 'right':
            self.head.orientation = (PLAYER_SIZE, 0)
        elif command == 'r':
            self.restart_game()

if __name__ == '__main__':
    SnakePlusPlusApp().run()