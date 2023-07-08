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

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    char = None
    bg = None
    rectangle_image = ObjectProperty(Image(source='images/bg2.zip',anim_delay=0.1))
    char_height = 0.05
    char_width = 0.2
    char_offset = .3

    velocity = 0
    step_velocity = 0.3
    obs_velcoity = 0.2

    obs_width = 0.05
    obs_height = 0.1

    NB_OBS = 1
    obs = []
    obs_images = ["images/asteroid.png", "images/missle.png", "images/burger.png"]

    world = None
    world_width = 1
    world_height = .03
    world_sprite = None
    collision_count = 0
    collision_circles = []
    collision_circle_size = 0.2

    score = 0
    level = 0

    first_obstacle_delay = 3.0
    game_start_time = 0.0
    first_obstacle_spawned = False

    menu_title = StringProperty("WORLD DEFENDER")
    menu_button = StringProperty("START")
    score_txt = StringProperty("SCORE")
    health_txt = StringProperty("HEALTH: 100%")
    menu_widget = ObjectProperty()
    health_counter = 100

    state_game_over = False
    state_game_start = False


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

    
    def reset_game(self):
        self.collision_count = 0
        self.level = 0
        self.score = 0
        self.health_counter = 100 
        self.score_txt = "SCORE: 0" 
        self.health_txt = "HEALTH: 100%"
        self.state_game_over = False
        self.first_obstacle_spawned = False
    
    
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

        char_image = "images/platform.png"
        char_texture = Image(source=char_image).texture
        self.char.texture = char_texture

            

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

        world_image = "images/world_color.png"
        world_texture = Image(source=world_image).texture
        self.world.texture = world_texture

        


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
        

        

        if not self.state_game_over and self.state_game_start:
            char_x = self.char.pos[0]
            char_x += self.velocity * time_factor
            char_y = self.char_offset * self.height
            self.char.pos = (char_x, char_y)
            for obstacle in self.obs:
                if not self.first_obstacle_spawned:
                    obstacle.pos = (self.width *2, self.height *2)
                    self.first_obstacle_spawned = True
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
            
            self.health_counter = self.health_counter
            if self.collides_with_world(obstacle):
                self.collision_count += 1
                self.health_counter -= 25
                self.health_txt = "HEALTH: " + str(self.health_counter) + "%"

                if self.health_counter == 0 and not self.state_game_over:
                    self.state_game_over = True
                    self.menu_widget.opacity = 1
                    self.menu_title = "GAME OVER"
                    self.menu_button = "RESTART"
                    self.game_over()


                print("Collision: "+ str(self.collision_count))
                self.reset_obstacle()
        
        
        #self.increase_level()

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
        if obstacle_image == "images/asteroid.png":
            print("asteroid")
            obstacle.size = (0.15*self.width, 0.15*self.width)
        
        elif obstacle_image == "images/missle.png":
            obstacle.size = (0.15*self.width, 0.2*self.width)


        elif obstacle_image == "images/burger.png":
            obstacle.size = (0.13*self.width, 0.1*self.width)
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


    def increase_level(self):
        self.level = self.score // 5 + 1

        self.obs_velcoity = 0.1 + self.level * 0.01

        if self.obs_velcoity >= 0.17:
            self.obs_velcoity = 0.17



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
    
    def on_menu_button_press(self): 
        print("Button")
        self.reset_game()
        self.state_game_start = True
        self.menu_widget.opacity = 0
    
        



class PlatformApp(App):
    pass

PlatformApp().run()
