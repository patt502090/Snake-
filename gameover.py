from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from sound import SoundControl

class GameOverPopup(Popup):
    #sound_control = SoundControl()
    def __init__(self, score, game_instance,muted, **kwargs):
        super(GameOverPopup, self).__init__(**kwargs)
        #self.sound_control.stop_sound()
        self.title = "Game Over"
        self.size_hint = (None, None)
        self.size = (400, 300)
        self.game_instance = game_instance
        self.muted = muted
        content_layout = BoxLayout(orientation="vertical")

        score_label = "Your Score: {}".format(max(score, 0))
        content_layout.add_widget(Label(text=score_label))

        close_button = Button(text="Restart Game")
        close_button.bind(on_press=self.close_and_restart)

        pre_button = Button(text="Back to Home Screen")
        pre_button.bind(on_press=self.pre_start)
        content_layout.add_widget(pre_button)
        content_layout.add_widget(close_button)

        self.content = content_layout

    def pre_start(self, instance):
        self.dismiss()                
        App.get_running_app().root.get_screen("start").pre_start(instance, self.game_instance.muted)
    
    def close_and_restart(self, instance):
        self.dismiss()        
        self.game_instance.sound_control.start_game_sound(self.muted)
        self.game_instance.start_game()
        

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        else:
            return False
