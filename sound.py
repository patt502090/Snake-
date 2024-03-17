from kivy.core.audio import SoundLoader

class SoundControl:
    def __init__(self):
        self.muted = False
        self.fruit_sound = SoundLoader.load("sounds/collide+.mp3")
        self.poison_fruit_sound = SoundLoader.load("sounds/collide-.mp3")
        self.lucky_fruit_sound = SoundLoader.load("sounds/collide_lucky.mp3")
        self.gameOver_sound = SoundLoader.load("sounds/gameOver.mp3")
        self.sound = SoundLoader.load("sounds/background.mp3")
    def start_game_sound(self, status):        
        self.sound.play()
        self.sound.loop = True
        if not status:
            self.muted = False
        if not self.muted:
            self.sound.volume = 0.5
        else:
            self.sound.volume = 0

    def stop_sound(self):
        if self.sound:
            self.sound.stop()

    def toggle_sound(self,pause,instance):
        self.pause = pause
        if self.sound:
            if not self.muted:                
                self.sound.volume = 0
                self.fruit_sound.volume = 0
                self.gameOver_sound.volume = 0
                self.poison_fruit_sound.volume = 0
                self.lucky_fruit_sound.volume = 0
                self.muted = True  
                instance.text = "Unmute"     
            else:
                if not self.pause:
                    self.sound.volume = 0.5
                    self.fruit_sound.volume = 0.5
                    self.gameOver_sound.volume = 0.5
                    self.poison_fruit_sound.volume = 0.5
                    self.lucky_fruit_sound.volume = 0.5
                    instance.text = "mute"
                    self.muted = False     

    def play_gameOver_sound(self):
        if self.gameOver_sound:
            self.gameOver_sound.play()              
