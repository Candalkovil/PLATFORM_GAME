from kivy.properties import Clock
from kivy.uix.relativelayout import RelativeLayout

def move_left(self):
    self.velocity = -self.step_velocity * self.width / 7


def move_right(self):
    self.velocity = self.step_velocity * self.width / 7


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left' or keycode[1] == 'a':
        self.move_left()
    elif keycode[1] == 'right' or keycode[1] == 'd':
        self.move_right()
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.velocity = 0
    return True

def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_start:
        if touch.x < self.width/2:
            self.move_left()
        else:
            self.move_right()
    
    return super(RelativeLayout, self).on_touch_down(touch)

def on_touch_up(self, touch):
    self.velocity = 0