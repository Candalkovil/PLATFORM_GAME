from kivy.config import Config
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '750')
import time
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle, Ellipse, Quad
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy import platform
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
import random
from kivy.graphics import Ellipse
from kivy.uix.scatter import Scatter



class MainWidget(RelativeLayout):
    char = None
    char_height = 0.05
    char_width = 0.2
    char_offset = .3

    velocity = 0
    step_velocity = 0.2
    obs_velcoity = 0.1

    obs_width = 0.05
    obs_height = 0.1

    NB_OBS = 1
    obs = []
    obs_images = ["images/asteroid.png", "images/earth.png", "images/ship.png"]

    world = None
    world_width = 1
    world_height = .03
    world_sprite = None
    collision_count = 0
    collision_circles = []
    collision_circle_size = 0.2

    score = 0

    first_obstacle_delay = 3.0
    game_start_time = 0.0
    first_obstacle_spawned = False

    score_txt = StringProperty("SCORE")
    health_txt = StringProperty("HEALTH: 100%")
    health_counter = 100


    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_char()
        self.init_obstacles()
        self.init_world()
        self.game_start_time = Clock.get_time()
   

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)
    
    
    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    

    def init_char(self):
        with self.canvas:
            self.char = Rectangle()
    
    def update_char(self):
        self.char.size = (self.char_width*self.width, self.char_height*self.height)
        if self.char.pos[0] >= self.width - self.char_width*self.width:
            y = self.char.pos[1]
            self.char.pos = (self.width - self.char_width*self.width,y)

        if self.char.pos[0] <= 0:
            y = self.char.pos[1]
            self.char.pos = (0,y)
            

    def init_obstacles(self):
        with self.canvas:
            for i in range(self.NB_OBS):
                self.obs.append(Rectangle(size=(0,0)))


    def init_world(self):
        with self.canvas:
            self.world = Rectangle()
        
        

    def update_world(self):

        self.world.size = (self.width, self.world_height * self.height)
        self.world.pos = (0, 0)

        


    def on_size(self, *args):
        self.update_char()
        for obstacle in self.obs:
            obstacle.pos = (obstacle.pos[0] * self.width / Window.size[0], obstacle.pos[1] * self.height / Window.size[1])



    
    def move_left(self):

        self.velocity = -self.step_velocity * self.height / 10
       
    
    def move_right(self):

        self.velocity = self.step_velocity * self.height / 10
       
    def update(self, dt):
        self.update_char()
        self.update_world()
        time_factor = dt * 60
        
        char_x = self.char.pos[0]
        char_x += self.velocity * time_factor
        char_y = self.char_offset * self.height
        self.char.pos = (char_x, char_y)

        for obstacle in self.obs:
            pos_y = obstacle.pos[1]
            pos_y -= self.obs_velcoity * time_factor * self.height / 10
            obstacle.pos = (obstacle.pos[0], pos_y)

            # Check collision with character
            if self.collides_with_char(obstacle):
                self.reset_obstacle()
                self.increment_score()

        # Check if obstacle is off the screen
        if pos_y + obstacle.size[1] < 0:
            self.reset_obstacle()
        
        if self.collides_with_world(obstacle):
            self.collision_count += 1
            self.health_counter -= 25
            self.health_txt = "HEALTH: " + str(self.health_counter) + "%"


            print("Collision: "+ str(self.collision_count))
            self.reset_obstacle()

    def collides_with_char(self, obstacle):
        char_left = self.char.pos[0]
        char_right = self.char.pos[0] + self.char.size[0]
        char_bottom = self.char.pos[1]
        char_top = self.char.pos[1] + self.char.size[1]

        obs_left = obstacle.pos[0]
        obs_right = obstacle.pos[0] + obstacle.size[0]
        obs_bottom = obstacle.pos[1]
        obs_top = obstacle.pos[1] + obstacle.size[1]

        # Check for collision
        if char_right > obs_left and char_left < obs_right and char_top > obs_bottom and char_bottom < obs_top:
            return True
        return False

    def collides_with_world(self, obstacle):
        world_left = self.world.pos[0]
        world_right = self.world.pos[0] + self.world.size[0]
        world_bottom = self.world.pos[1]
        world_top = self.world.pos[1] + self.world.size[1]

        obs_left = obstacle.pos[0]
        obs_right = obstacle.pos[0] + obstacle.size[0]
        obs_bottom = obstacle.pos[1]
        obs_top = obstacle.pos[1] + obstacle.size[1]

        # Check for collision
        if world_right > obs_left and world_left < obs_right and world_top > obs_bottom:
            self.spawn_collision_circle(obstacle.pos)
            return True
        return False

    
    def reset_obstacle(self):
        obstacle_image = random.choice(self.obs_images)
        obstacle_texture = Image(source=obstacle_image).texture
        #aspect_ratio = obstacle_texture.width / obstacle_texture.height
        #obstacle_height = self.height * 0.2
        #obstacle_width = obstacle_height * aspect_ratio

        obstacle = self.obs[0]
        obstacle.texture = obstacle_texture
        obstacle.size = (self.obs_width*self.width, self.obs_height*self.height)
        obstacle.pos = (random.randint(0, int(self.width) - int(obstacle.size[0])), int(self.height))
    

    def spawn_collision_circle(self, position):
        circle_image = Image(source='images/ex.png')
        circle_image.size_hint = (None, None)
        circle_image.size = (self.collision_circle_size*self.height, self.collision_circle_size*self.height)  # Set the desired size of the collision image

        scatter = Scatter(
            size_hint=(None, None),
            size=circle_image.size,
            do_translation=False  # Disable translation to manually set the position
        )

        scatter.add_widget(circle_image)
        self.collision_circles.append(scatter)
        self.add_widget(scatter)

        offset_x = circle_image.width / 2
        offset_y = self.height * 0.05

        scatter.pos = (position[0] - offset_x, position[1] - offset_y)

        Clock.schedule_once(lambda dt: self.remove_collision_circle(scatter), 1.0)



    def remove_collision_circle(self, circle):
        self.remove_widget(circle)
        self.collision_circles.remove(circle)




    def increment_score(self):
        self.score += 1
        self.score_txt = "SCORE: " + str(self.score)
        print(self.score)
        
    
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

    def game_over(self):
        print("Game Over")  # Placeholder for game over logic



class PlatformApp(App):
    pass

PlatformApp().run()
