import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty
from random import randint
from kivy.vector import Vector
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.popup import Popup
import os
from kivy.uix.filechooser import FileChooserListView
import functools
from kivy.properties import StringProperty, ListProperty
import random
from kivy.uix.image import AsyncImage
from os.path import basename
from kivy.uix.colorpicker import ColorPicker
from gameover import GameOverPopup
from smartgrid import smartGrid
from sound import SoundControl

Config.set("graphics", "width", "900")
Config.set("graphics", "height", "600")

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 900
PLAYER_SIZE = 50
SPEED = 0.155
TOP_SCORE_FILE = "top_score.txt"


# กำหนดหน้าจอเริ่มต้น
class StartScreen(Screen):
    # ส่วนต่าง ๆ ของหน้าจอเริ่มต้น
    countdown_label = ObjectProperty(None)
    start_button = ObjectProperty(None)
    top_score_label = ObjectProperty(None)
    file_chooser_button = ObjectProperty(None)
    exit_button = ObjectProperty(None)
    color_button = ObjectProperty(None)
    file_chooser_popup = None
    top_score_label = None
    muted = False

    # เริ่มต้นเกม
    def pre_start(self, instance, muted):
        if self.background_rect is not None:
            self.canvas.before.remove(self.background_rect)
        self.start_button.opacity = 1
        self.file_chooser_button.opacity = 1
        self.exit_button.opacity = 1
        self.start_button.disabled = False
        self.file_chooser_button.disabled = False
        self.muted = muted
        self.exit_button.disabled = False
        self.color_button.disabled = False
        self.color_button.opacity = 1
        self.top_score_label.opacity = 1
        App.get_running_app().root.transition.direction = "right"
        App.get_running_app().root.current = "start"

    # เปิด file chooser เพื่อเลือกรูปภาพ
    def open_filechooser(self):
        self.file_chooser = FileChooserListView(filters=["*.jpg", "*.png"])
        self.file_chooser.bind(on_submit=functools.partial(self.select_image))
        self.file_chooser_popup = Popup(
            title="Choose an image file",
            content=self.file_chooser,
            size_hint=(0.9, 0.9),
        )
        close_button = Button(text="Close", size_hint_y=None, height=40)
        close_button.bind(on_press=self.file_chooser_popup.dismiss)
        self.file_chooser_popup.content.add_widget(close_button)
        self.file_chooser_popup.open()

    # เลือกรูปภาพและบันทึก
    def select_image(self, *args):
        selected_file = args[1]
        if selected_file:
            image_path = selected_file[0]
            image_name = basename(image_path)
            popup_content = BoxLayout(orientation="vertical")
            image = AsyncImage(source=image_path)
            popup_content.add_widget(image)
            popup_content.add_widget(Label(text=f"{image_name}", size_hint=(1, 0.5)))

            button_layout = BoxLayout(size_hint_y=None, height=50)
            save_button = Button(text="Save")
            cancel_button = Button(text="Cancel")

            save_button.bind(
                on_press=lambda instance: self.save_image_and_close(popup, image_path)
            )

            button_layout.add_widget(save_button)
            button_layout.add_widget(cancel_button)
            popup_content.add_widget(button_layout)
            popup = Popup(
                title="Save or Not?",
                content=popup_content,
                size_hint=(None, None),
                size=(400, 400),
            )
            cancel_button.bind(on_press=popup.dismiss)
            popup.open()

    # บันทึกรูปและปิด popup
    def save_image_and_close(self, popup, image_path):
        self.manager.get_screen("game").update_snake_head_image(image_path)
        self.manager.get_screen("game").play_button_click_sound()
        popup.title = "Save image successful"
        self.file_chooser_popup.dismiss()
        Clock.schedule_once(popup.dismiss, 0.5)

    # เมื่อเข้าหน้าจอ
    def on_enter(self, *args):
        top_score = load_top_score()
        self.top_score_label.text = f"Top Score: {top_score}"

    # เริ่มนับถอยหลังก่อนเริ่มเกม
    def start_game_countdown(self):
        self.start_button.opacity = 0
        self.file_chooser_button.opacity = 0
        self.top_score_label.opacity = 0
        self.exit_button.opacity = 0
        self.start_button.disabled = True
        self.file_chooser_button.disabled = True
        self.exit_button.disabled = True
        self.color_button.disabled = True
        self.color_button.opacity = 0

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)

        Clock.schedule_once(lambda dt: setattr(self.countdown_label, "text", "3"), 1)
        Clock.schedule_once(lambda dt: setattr(self.countdown_label, "text", "2"), 2)
        Clock.schedule_once(lambda dt: setattr(self.countdown_label, "text", "1"), 2.98)
        Clock.schedule_once(
            lambda dt: setattr(self.countdown_label, "text", "Go Go Go"), 3.5
        )
        Clock.schedule_once(lambda dt: setattr(self.countdown_label, "text", ""), 3.69)
        Clock.schedule_once(self.start_game, 3.7)

    # เริ่มเกม
    def start_game(self, dt):
        self.manager.current = "game"
        sound = not self.muted
        self.manager.get_screen("game").sound_control.start_game_sound(sound)
        self.manager.get_screen("game").start_game()

    # เปิด color picker เพื่อเลือกสีหางงู
    def open_color_picker(self):
        popup_content = BoxLayout(orientation="vertical")

        color_picker = ColorPicker()
        popup_content.add_widget(color_picker)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        save_button = Button(text="Save", size_hint_x=0.5)
        cancel_button = Button(text="Cancel", size_hint_x=0.5)

        def save_color(instance):
            snake_tail_color = color_picker.color
            self.manager.get_screen("game").play_button_click_sound()
            self.manager.get_screen("game").set_snake_tail_color(snake_tail_color)
            popup.dismiss()

        save_button.bind(on_press=save_color)

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)

        popup_content.add_widget(button_layout)

        popup = Popup(
            title="Select Snake Tail Color",
            content=popup_content,
            size_hint=(None, None),
            size=(500, 450),
        )
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()


# กำหนดหน้าจอเกม
class SnakeHead(Widget):
    orientation = (PLAYER_SIZE, 0)  # กำหนดทิศทางเริ่มต้นของหัวงู
    source = StringProperty("image/snake2.png")  # กำหนดรูปภาพของหัวงู

    def reset_pos(self):
        # รีเซ็ตตำแหน่งของหัวงูไปที่กลางของหน้าต่างหรือวางตำแหน่งผู้เล่นไว้ตรงกลางกระดานเกม
        self.pos = [
            int(Window.width / 2 - (Window.width / 2 % PLAYER_SIZE)),
            int(Window.height / 2 - (Window.height / 2 % PLAYER_SIZE)),
        ]
        self.orientation = (PLAYER_SIZE, 0)  # รีเซ็ตทิศทางของหัวงูให้เป็นเริ่มต้นอีกครั้ง

    def move(self):
        # เลื่อนหัวงูไปในทิศทางที่ระบุโดย 'orientation' โดยการเคลื่อนที่ด้วย Vector
        self.pos = Vector(*self.orientation) + self.pos


class Fruit(Widget):
    def move(self, new_pos):
        # เคลื่อนย้ายตำแหน่งของผลแอปเปิ้ลไปยังตำแหน่งใหม่ที่กำหนด
        self.pos = new_pos


class PoisonFruit(Widget):
    def move(self, new_pos):
        # เคลื่อนย้ายตำแหน่งของผลพิษไปยังตำแหน่งใหม่ที่กำหนด
        self.pos = new_pos


class LuckyFruit(Widget):
    def move(self, new_pos):
        # เคลื่อนย้ายตำแหน่งของผลลุ้นโชคไปยังตำแหน่งใหม่ที่กำหนด
        self.pos = new_pos


# ฟังก์ชันหลักของโปรแกรม
class SnakePlusPlusApp(App):
    # สร้างแอป
    def build(self):
        Window.size = (900, 600)
        sm = ScreenManager()
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(SnakeGame(name="game"))

        return sm


class SnakeTail(Widget):
    color = ListProperty([0.5, 1.0, 1, 1])

    def move(self, new_pos):
        # เคลื่อนย้ายตำแหน่งของหางงูไปยังตำแหน่งใหม่
        self.pos = new_pos


def save_top_score(score):
    # บันทึกคะแนนสูงสุดลงในไฟล์
    with open(TOP_SCORE_FILE, "w") as file:
        file.write(str(score))


def load_top_score():
    # โหลดคะแนนสูงสุดจากไฟล์หากมี
    if os.path.exists(TOP_SCORE_FILE):
        with open(TOP_SCORE_FILE, "r") as file:
            content = file.read().strip()
            if content:
                return int(content)
    return 0


class SnakeGame(Screen):
    # ส่วนต่าง ๆ ของหน้าจอเกม
    fruit = ObjectProperty(None)
    poison_fruit = ObjectProperty(None)
    lucky_fruit = ListProperty([])
    head = ObjectProperty(None)
    sound = None
    muted = False
    score = NumericProperty(0)
    last_score = NumericProperty(0)
    top_score = NumericProperty(load_top_score())
    player_size = NumericProperty(PLAYER_SIZE)
    ck = False
    color = ObjectProperty(None)
    sound_control = SoundControl()

    # กำหนดค่าเริ่มต้น
    def __init__(self, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)

        Window.bind(on_key_down=self.key_action)

        if PLAYER_SIZE < 3:
            raise ValueError("ขนาดโปรแกรมเล่นควรมีอย่างน้อย 3 px")

        if WINDOW_HEIGHT < 3 * PLAYER_SIZE or WINDOW_WIDTH < 3 * PLAYER_SIZE:
            raise ValueError("ขนาดหน้าต่างต้องมีขนาดใหญ่กว่าขนาดเครื่องเล่นอย่างน้อย 3 เท่า")

        self.tail = []
        self.count_pause = 0
        self.sound = SoundLoader.load("sounds/background.mp3")
        self.sound_pos = None
        self.color = [0.5, 1.0, 1, 1]
        self.pauses = False

        # กำหนดค่าคะแนนเริ่มต้นสำหรับการสุ่มเกิดผลลุ้นโชคแรก
        self.initial_random_score = randint(1, 8)

    # กำหนดสีของหางงู
    def set_snake_tail_color(self, color):
        self.color = color

    # เริ่มเกม
    def start_game(self):
        self.last_score = 0
        # เริ่มต้นการตั้งเวลาในการอัปเดตสถานะเกมด้วยความเร็ว SPEED
        self.timer = Clock.schedule_interval(self.refresh, SPEED)
        # ล้างหางของงูและเริ่มเกมใหม่
        self.tail = []
        self.restart_game()

    # อัปเดตสถานะของเกมโดยตรวจสอบคะแนนและตำแหน่งของสิ่งต่าง ๆ
    def refresh(self, dt):

        # ส่วนของการสุ่มการเกิดผลลุ้นโชค
        if self.score == self.initial_random_score and not self.lucky_fruit:
            self.initial_random_score = randint(self.score + 1, self.score + 8)
            self.spawn_lucky_fruit()

        # ส่วนของการสุ่มการเกิดผลพิษ
        if self.score <= 5 and self.score % 5 == 0 and self.score != self.last_score:
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif self.score > 5 and self.score % 4 == 0 and self.score != self.last_score:
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif self.score > 10 and self.score % 3 == 0 and self.score != self.last_score:
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif (
            self.score > 15
            and self.score <= 25
            and self.score % 2 == 0
            and self.score != self.last_score
        ):
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif self.score > 25 and self.score % 1 == 0 and self.score != self.last_score:
            self.last_score = self.score
            self.spawn_poison_fruit()

        if self.score <= 5 and self.score % 5 == 0 and self.score != self.last_score:
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif (
            self.score > 5
            and self.score <= 10
            and self.score % 4 == 0
            and self.score != self.last_score
        ):
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif (
            self.score > 10
            and self.score <= 15
            and self.score % 3 == 0
            and self.score != self.last_score
        ):
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif (
            self.score > 15
            and self.score <= 25
            and self.score % 2 == 0
            and self.score != self.last_score
        ):
            self.last_score = self.score
            self.spawn_poison_fruit()

        elif self.score > 25 and self.score % 1 == 0 and self.score != self.last_score:
            self.last_score = self.score
            self.spawn_poison_fruit()

        # ตรวจสอบว่าหัวงูชนขอบเขตหรือกินตัวเองหรือไม่
        if not (0 <= self.head.pos[0] < WINDOW_WIDTH) or not (
            20 <= self.head.pos[1] < WINDOW_HEIGHT
        ):
            self.break_game()
            return

        if self.occupied[self.head.pos] is True:
            self.break_game()
            return

        # เคลื่อนที่ของงูและอัปเดตตำแหน่งของหาง
        self.occupied[self.tail[-1].pos] = False
        self.tail[-1].move(self.tail[-2].pos)

        for i in range(2, len(self.tail)):
            self.tail[-i].move(new_pos=(self.tail[-(i + 1)].pos))

        self.tail[0].move(new_pos=self.head.pos)
        self.occupied[self.tail[0].pos] = True

        self.head.move()

        # ส่วนของการตรวจสอบการชนกับผลแอปเปิ้ล
        if self.head.pos == self.fruit.pos:
            if self.sound_control.fruit_sound:
                self.sound_control.fruit_sound.play()
            self.score += 1
            self.score_label.text = f"Score: {self.score}"
            self.tail.append(
                SnakeTail(pos=self.head.pos, size=self.head.size, color=self.color)
            )
            self.add_widget(self.tail[-1])
            self.spawn_fruit()

        # ส่วนของการตรวจสอบการชนกับผลพิษ
        elif self.poison_fruit and self.head.pos == self.poison_fruit.pos:
            if self.sound_control.poison_fruit_sound:
                self.sound_control.poison_fruit_sound.play()
            self.score -= 3
            self.score_label.text = f"Score: {self.score}"
            if self.score < 0:
                self.break_game()
            else:
                new_tail_positions = [
                    (self.head.pos[0] + (i + 1) * PLAYER_SIZE, self.head.pos[1])
                    for i in range(2)
                ]
                # เพิ่มตำแหน่งของหางใหม่
                for pos in new_tail_positions:
                    self.tail.append(SnakeTail(pos=pos, size=self.head.size))
                    self.add_widget(self.tail[-1])

                self.spawn_poison_fruit()

        # ส่วนของการตรวจสอบการชนกับผลลุ้นโชค
        elif any(self.head.pos == fruit.pos for fruit in self.lucky_fruit):
            if self.sound_control.lucky_fruit_sound:
                self.sound_control.lucky_fruit_sound.play()
            score_change = randint(-5, 5)
            self.score += score_change
            self.score_label.text = f"Score: {self.score}"
            if self.score < 0:
                self.break_game()
            else:
                tail_change = randint(1, 3)
                if tail_change > 0:
                    for _ in range(tail_change):
                        new_tail_pos = (
                            self.head.pos[0] + len(self.tail) * PLAYER_SIZE,
                            self.head.pos[1],
                        )
                        new_tail = SnakeTail(pos=new_tail_pos, size=self.head.size)
                        self.tail.append(new_tail)
                        self.add_widget(new_tail)
                        self.occupied[new_tail_pos] = True
                elif tail_change < 0:
                    for _ in range(abs(tail_change)):
                        if len(self.tail) > 0:
                            removed_tail = self.tail.pop()
                            self.remove_widget(removed_tail)
                            self.occupied[removed_tail.pos] = False

            # ลบ lucky fruit ที่ชนออกจากการแสดงผล
            for fruit in self.lucky_fruit:
                self.remove_widget(fruit)
            self.lucky_fruit = []

        # ส่วนของการปรับระดับความยากของเกม
        if self.count_pause >= 7:
            self.timer.cancel()
            self.timer = Clock.schedule_interval(self.refresh, 0.04)
        elif self.score >= 10:
            self.timer.cancel()
            self.timer = Clock.schedule_interval(self.refresh, 0.1)
        elif self.score >= 5:
            self.timer.cancel()
            self.timer = Clock.schedule_interval(self.refresh, 0.127)

        # print("score", self.score)
        # print("top", self.top_score)
        if self.score > self.top_score:
            self.top_score = self.score
            self.top_score_label.text = (
                f"Top Score: {str(self.score)}"  # แสดงคะแนนสูงสุดใหม่
            )

    # เล่นเสียงการคลิกปุ่ม และแสดงแถบคะแนน
    def play_button_click_sound(self):
        button_click_sound = SoundLoader.load("sounds/clickbutton.wav")
        button_click_sound.volume = 0.28
        if button_click_sound:
            button_click_sound.play()

        # Score box
        self.score_box = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            height=50,
            width=Window.width,
        )

        with self.score_box.canvas:
            Color(0, 0, 0)  # สีดำ
            self.score_background = Rectangle(
                pos=self.score_box.pos, size=self.score_box.size
            )

        self.score_label = Label(
            text=f"Score: {self.score}", size_hint=(None, None), height=50
        )
        self.score_box.add_widget(self.score_label)

        # Top Score label
        self.top_score_label = Label(
            text=f"Top Score: {self.top_score}",
            size_hint=(None, None),
            height=50,
            width=300,
        )
        self.score_box.add_widget(self.top_score_label)

        # Mute button
        self.mute_button = Button(text="Mute", size_hint=(None, None), size=(100, 50))
        self.mute_button.bind(on_press=self.toggle_sound)
        self.pause = Button(text="pause", size_hint=(None, None), size=(100, 50))
        self.pause.bind(on_press=self.pause_game)
        self.score_box.add_widget(self.mute_button)
        self.score_box.add_widget(self.pause)
        self.add_widget(self.score_box)

        self.mute_button.pos = (
            Window.width - self.mute_button.width,
            Window.height - self.mute_button.height,
        )

    # หยุดหรือเริ่มเกมใหม่โดยตรวจสอบสถานะปัจจุบันของเกม
    def pause_game(self, instance):
        if self.timer.is_triggered:  # ตรวจสอบว่าเกมถูกหยุดหรือไม่
            self.pauses = True
            self.count_pause += 1
            self.timer.cancel()  # หยุดตัวจับเวลา
            if not self.muted:
                self.sound.volume = 0  # ปรับระดับเสียงลงเป็น 0 เมื่อหยุดเกม
        else:
            self.timer()
            self.pauses = False
            if not self.muted:
                self.sound.volume = 0.5  # ปรับระดับเสียงเป็น 0.5 เมื่อเริ่มเกมใหม่

    # เปิดหรือปิดเสียง
    def toggle_sound(self, instance):
        self.sound_control.toggle_sound(self.pauses, instance)

    # สร้างผลแอปเปิ้ลใหม่โดยการสุ่มตำแหน่งใหม่จนกว่าจะได้ตำแหน่งที่ไม่ถูกบดบังโดยสิ่งอื่นในเกม
    def spawn_fruit(self):
        roll = self.fruit.pos
        found = False
        while not found:
            # สุ่มตำแหน่งใหม่สำหรับผลแอปเปิ้ล
            roll = [
                PLAYER_SIZE * randint(0, int(WINDOW_WIDTH / PLAYER_SIZE) - 1),
                PLAYER_SIZE * randint(0, int(WINDOW_HEIGHT / PLAYER_SIZE) - 1),
            ]
            # ตรวจสอบว่าตำแหน่งที่สุ่มได้ไม่ตรงกับสิ่งอื่นในเกมและไม่ตรงกับหัวงู
            if self.occupied[roll] is True or roll == self.head.pos:
                continue
            found = True
            # ตรวจสอบว่าตำแหน่ง Y ที่สุ่มได้ไม่ได้อยู่บนขอบด้านล่างของหน้าจอ
            if roll[1] == 0:
                found = False
            # ตรวจสอบว่าตำแหน่ง X ที่สุ่มได้ไม่เกินขอบด้านขวาของหน้าจอ
            if roll[0] == 1050:
                found = False
        self.fruit.move(roll)

    # สร้างผลพิษ
    def spawn_poison_fruit(self):
        # ถ้ายังไม่มีผลพิษ ให้สร้างและเพิ่มลงในหน้าจอ
        if self.poison_fruit is None:
            self.poison_fruit = PoisonFruit()
            self.add_widget(self.poison_fruit)

        # ค้นหาตำแหน่งที่จะวางผลพิษ บนกริดเกมที่ไม่มีสิ่งกีดขวางอื่น ๆ และไม่ตรงกับตำแหน่งของหัวงูหรือผลไม้อื่นๆ
        roll = self.poison_fruit.pos
        found = False
        while not found:
            # สุ่มตำแหน่งใหม่สำหรับผลพิษ
            roll = [
                PLAYER_SIZE * randint(0, int(WINDOW_WIDTH / PLAYER_SIZE) - 1),
                PLAYER_SIZE * randint(0, int(WINDOW_HEIGHT / PLAYER_SIZE) - 1),
            ]
            if (
                not self.occupied[roll]
                and roll != self.head.pos
                and roll != self.fruit.pos
                and roll != self.lucky_fruit
            ):
                found = True
            # ตรวจสอบว่าตำแหน่ง Y ที่สุ่มได้ไม่ได้อยู่บนขอบด้านล่างของหน้าจอ
            if roll[1] == 0:
                found = False
            # ตรวจสอบว่าตำแหน่ง X ที่สุ่มได้ไม่เกินขอบด้านขวาของหน้าจอ
            if roll[0] == 1050:
                found = False

        # ย้าย Poison Fruit ไปยังตำแหน่งที่สุ่มได้
        self.poison_fruit.move(roll)

    # สร้างผลลุ้นโชค
    def spawn_lucky_fruit(self):
        # สร้างผลลุ้นโชคใหม่และเพิ่มลงใน list ของ lucky_fruit
        new_lucky_fruit = LuckyFruit()
        self.lucky_fruit.append(new_lucky_fruit)
        self.add_widget(new_lucky_fruit)

        # เล่นเสียงเมื่อผลลุ้นโชค ถูกสร้างขึ้น
        if self.sound_control.spawn_lucky_fruit_sound:
            self.sound_control.spawn_lucky_fruit_sound.play()

        # ค้นหาตำแหน่งที่จะวาง Lucky Fruit บนกริดเกมที่ไม่มีสิ่งกีดขวางอื่น ๆ
        found = False
        while not found:
            # สุ่มตำแหน่งใหม่สำหรับผลลุ้นโชค
            roll = [
                PLAYER_SIZE * random.randint(0, int(WINDOW_WIDTH / PLAYER_SIZE) - 1),
                PLAYER_SIZE * random.randint(0, int(WINDOW_HEIGHT / PLAYER_SIZE) - 1),
            ]

            # ตรวจสอบว่าตำแหน่งที่สุ่มได้ไม่มีสิ่งกีดขวางและไม่ตรงกับตำแหน่งของหัวงูหรือผลไม้หรือผลไม้พิษ
            if (
                not self.occupied[roll]
                and roll != self.head.pos
                and roll != self.fruit.pos
                and roll != self.poison_fruit.pos
            ):
                found = True

            # ตรวจสอบว่าตำแหน่ง Y ที่สุ่มได้ไม่ได้อยู่บนขอบด้านล่างของหน้าจอ
            if roll[1] == 0:
                found = False
            # ตรวจสอบว่าตำแหน่ง X ที่สุ่มได้ไม่เกินขอบด้านขวาของหน้าจอ
            if roll[0] == 1050:
                found = False
        # ย้าย Lucky Fruit ไปยังตำแหน่งที่สุ่มได้
        new_lucky_fruit.move(roll)

    # จบเกม
    def break_game(self):
        # แสดง Popup เมื่อเกมจบพร้อมกับส่งค่าคะแนนและตัวเกมเพื่อให้ Popup แสดงค่าคะแนนให้ผู้เล่น
        score_popup = GameOverPopup(
            score=self.score, game_instance=self, muted=self.sound_control.muted
        )
        score_popup.open()

        # เล่นเสียง Game Over
        self.sound_control.play_gameOver_sound()

        # หยุดเสียงพื้นหลัง
        self.sound_control.stop_sound()

        # ลบตัวแทนของหางงูออกจากการแสดงผล
        for block in self.tail:
            self.remove_widget(block)

        # ยกเลิกการตั้งเวลาในเกม
        self.timer.cancel()
        self.mute_button.disabled = True
        self.pause.disabled = True

        # ลบผลลุ้นโชค ออกจากการแสดงผล (ถ้ามี)
        if self.lucky_fruit:
            for fruit in self.lucky_fruit:
                self.remove_widget(fruit)
            self.lucky_fruit = []

        # บันทึกคะแนนที่สูงที่สุดเมื่อมีคะแนนใหม่ที่มากกว่าคะแนนสูงที่สุดเก่า
        if self.score > load_top_score():
            save_top_score(self.score)

        # รีเซ็ตคะแนนใหม่เป็น 0 และอัปเดตค่าใน Score Label
        self.score = 0
        self.last_score = 0
        self.score_label.text = f"Score: {self.score}"

        self.lucky_number = -1

    # อัปเดตรูปภาพของหัวงู
    def update_snake_head_image(self, image_source):
        self.head.source = image_source

    # เริ่มเกมใหม่
    def restart_game(self):
        # รีเซ็ตตัวแปรที่เกี่ยวข้องกับการหยุดเกม
        self.count_pause = 0
        self.pause.disabled = False
        self.mute_button.disabled = False

        # สร้างตารางที่เก็บข้อมูลเกี่ยวกับตำแหน่งของตัวแทนต่างๆในเกม
        self.occupied = smartGrid()

        # เริ่มตั้งค่าตัวแปรเพื่อการทำงานของเกม
        self.timer.cancel()  # ยกเลิกการตั้งเวลา
        self.timer = Clock.schedule_interval(self.refresh, SPEED)  # ตั้งเวลาเริ่มต้นเกมใหม่
        self.head.reset_pos()  # รีเซ็ตตำแหน่งหัวงูกลับไปที่ตำแหน่งเริ่มต้น
        self.score = 0  # รีเซ็ตค่าคะแนนเริ่มต้นเป็น 0

        # สร้างตัวแทนของหางงู
        self.tail = []
        self.tail.append(
            SnakeTail(
                pos=(
                    self.head.pos[0] - PLAYER_SIZE,
                    self.head.pos[1],
                ),  # ตำแหน่งเริ่มต้นของหางงูที่ห่างจากหัวงู 1 ช่อง
                size=(self.head.size),  # ขนาดของหางงูเท่ากับขนาดของหัวงู
                color=self.color,  # สีของหางงู
            )
        )
        self.add_widget(self.tail[-1])  # เพิ่มหางงูลงในเกม
        self.occupied[self.tail[-1].pos] = True  # บันทึกตำแหน่งของหางงูในตาราง

        # สร้างหางงูที่สอง
        self.tail.append(
            SnakeTail(
                pos=(
                    self.head.pos[0] - 2 * PLAYER_SIZE,
                    self.head.pos[1],
                ),  # ตำแหน่งเริ่มต้นของหางงูที่ห่างจากหัวงู 2 ช่อง
                size=(self.head.size),  # ขนาดของหางงูเท่ากับขนาดของหัวงู
                color=self.color,  # สีของหางงู
            )
        )
        self.add_widget(self.tail[-1])  # เพิ่มหางงูลงในเกม
        self.occupied[self.tail[1].pos] = True  # บันทึกตำแหน่งของหางงูในตาราง
        self.spawn_fruit()  # สร้างผลแอปเปิ้ลใหม่ในเกม
        self.spawn_poison_fruit()  # สร้างผลพิษใหม่ในเกม

    # รับคำสั่งจากแป้นพิมพ์
    def key_action(self, *args):
        command = list(args)[3]  # ดึงคำสั่งที่ถูกส่งมาผ่านพารามิเตอร์ args
        if command == "w" or command == "up":
            self.head.orientation = (
                0,
                PLAYER_SIZE,
            )  # ถ้าเป็นคำสั่ง "w" หรือ "up" ให้งูเคลื่อนไปด้านบน
        elif command == "s" or command == "down":
            self.head.orientation = (
                0,
                -PLAYER_SIZE,
            )  # ถ้าเป็นคำสั่ง "s" หรือ "down" ให้งูเคลื่อนไปด้านล่าง
        elif command == "a" or command == "left":
            self.head.orientation = (
                -PLAYER_SIZE,
                0,
            )  # ถ้าเป็นคำสั่ง "a" หรือ "left" ให้งูเคลื่อนไปด้านซ้าย
        elif command == "d" or command == "right":
            self.head.orientation = (
                PLAYER_SIZE,
                0,
            )  # ถ้าเป็นคำสั่ง "d" หรือ "right" ให้งูเคลื่อนไปด้านขวา


if __name__ == "__main__":
    # รันแอป
    SnakePlusPlusApp().run()
