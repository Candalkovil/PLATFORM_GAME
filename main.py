import kivy
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '640')
Config.set('graphics', 'height', '960')
kivy.require('2.2.1')
from kivy.app import App
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import Clock, ObjectProperty, StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy import platform
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
import random
from kivy.uix.scatter import Scatter



Builder.load_file("menu.kv")
Builder.load_file("pause_menu.kv")
Builder.load_file("extras.kv")

class MainWidget(RelativeLayout):
    from user_actions import move_left, move_right, keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up
    from game_extras import increase_level, increment_score, game_over
    # User Creation
    char = None

    rectangle_image = ObjectProperty(Image(source='images/bg_pixel.png', anim_delay=0.1))

    # Set Images
    obs_images = ["images/meteor_main.png", "images/missile_main.png", "images/dragon.png", "images/burger.png"]
    impact_images = ["images/impact1.png", "images/impact2.png"]
    collision_circle_img = "images/ex.png"
    collision_ellipse_img = "images/blue.png"
    char_img = "images/platform_main.png"
    world_img = "images/world_color.png"
    music_file = "audio/main_music.wav"
    comic_img = "images/pow.png"


    enable_music = True

    # External kv properties
    menu_title = StringProperty("WORLD DEFENDER")
    menu_button = StringProperty("START")
    score_txt = StringProperty("SCORE")
    health_txt = StringProperty("HEALTH: 100%")
    highscore_txt = StringProperty("HIGHSCORE")
    music_img = StringProperty("images/music.png")
    music_txt = StringProperty("MUSIC: ON")
    vfx_text = StringProperty("VFX: ON")
    pause_txt = StringProperty("")
    menu_widget = ObjectProperty()
    pause_widget = ObjectProperty()
    extras_widget = ObjectProperty()
    

    # User properties
    char_height = 0.07
    char_width = 0.27
    char_offset = .3

    # user and obstacle velocity
    velocity = 0
    step_velocity = 0.3
    obs_velocity = 0.2

    # Obstacle Properties
    obs_width = 0.05
    obs_height = 0.1

    # User to Obstacle Collision Ellipse
    collision_ellipses = []
    collision_ellipse_width = 0.3
    collision_ellipse_height = 0.2

    collision_comic = []
    collision_comic_size = 0.1

    # Obs generation
    NB_OBS = 1
    obs = []

    # World and Obstacle Collision properties
    world = None
    world_width = 1
    world_height = .03
    collision_count = 0
    collision_circles = []
    collision_circle_size = 0.2

    vfx_option = True

    # Score metrics
    high_score = 0
    score = 0
    level = 0
    health_counter = 100

    #
    first_obstacle_delay = 3.0
    game_start_time = 0.0
    first_obstacle_spawned = False
    state_game_over = False
    state_game_start = False
    state_game_pause = False
    show_pause_button = False
    show_extras_button = False

    sound_impact = None
    sound_music = None
    music_position = 0
    mute_music = False

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # Initializing game features
        self.init_audio()
        self.init_char()
        self.init_obstacles()
        self.init_world()

        self.game_start_time = Clock.get_time()
        print(kivy.__version__ )
        

        

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        # 60 FPS
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def init_audio(self):
        # Audio init and volume control
        if self.enable_music:
            self.sound_music = SoundLoader.load(self.music_file)
        

            self.sound_music.volume = 1
            self.music_position = 0

       

    def reset_game(self):
        # Variables reset after game
        self.collision_count = 0
        self.level = 0
        self.score = 0
        self.health_counter = 100
        self.score_txt = "SCORE: 0"
        self.health_txt = "HEALTH: 100%"
        self.obs_velocity = 0.2
        self.step_velocity = 0.3
        self.state_game_over = False
        self.first_obstacle_spawned = False

    def is_desktop(self):
        # platform confirm
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_char(self):
        # Init for user character
        with self.canvas:
            self.char = Rectangle()

    def update_char(self):
        # Update Main User properties
        self.char.size = (self.char_width * self.width, self.char_height * self.height)
        if self.char.pos[0] >= self.width - self.char_width * self.width:
            y = self.char.pos[1]
            self.char.pos = (self.width - self.char_width * self.width, y)

        if self.char.pos[0] <= 0:
            y = self.char.pos[1]
            self.char.pos = (0, y)

        char_texture = Image(source=self.char_img).texture
        self.char.texture = char_texture

    def init_obstacles(self):
        # Init for Obstacles
        with self.canvas:
            for i in range(self.NB_OBS):
                self.obs.append(Rectangle(size=(0, 0)))

    def init_world(self):
        # Init for Rectangle Below
        with self.canvas:
            self.world = Rectangle()

    def update_world(self):
        # Main properties for world/rectangle
        self.world.size = (self.width, self.world_height * self.height)
        self.world.pos = (0, 0)

        world_texture = Image(source=self.world_img).texture
        self.world.texture = world_texture

    def on_size(self, *args):
        # Resize canvas for window change
        self.update_char()
        for obstacle in self.obs:
            obstacle.pos = (
                obstacle.pos[0] * self.width / Window.size[0],
                obstacle.pos[1] * self.height / Window.size[1],
            )

    def update(self, dt):
        '''
        Main function in game. All major update procedures go through this function.
        Includes Collision Logic between player, world and obstacles.
        Includes controls for game over and in-game displays.
        Includes feature to reset game.
        Includes movement feature for user.
        '''
        self.update_char()
        time_factor = dt * 60
        
        if self.show_pause_button:
            self.pause_widget.opacity = 1
            
        else:
            self.pause_widget.opacity = 0
            
        
        if not self.state_game_pause:
            self.extras_widget.opacity = 0
            self.update_world()
            if not self.state_game_over and self.state_game_start:
                if self.sound_music.state == "stop" and not self.mute_music:
                    self.sound_music.play()
                char_x = self.char.pos[0]
                char_x += self.velocity * time_factor
                char_y = self.char_offset * self.height
                self.char.pos = (char_x, char_y)
                for obstacle in self.obs:
                    if not self.first_obstacle_spawned:
                        obstacle.pos = (self.width * 2, self.height * 2)
                        self.first_obstacle_spawned = True
                    pos_y = obstacle.pos[1]
                    pos_y -= self.obs_velocity * time_factor * self.height / 10
                    obstacle.pos = (obstacle.pos[0], pos_y)

                    # Check collision with character
                    if self.collides_with_char(obstacle):
                        self.reset_obstacle()
                        self.increment_score()
                        if self.score > 20:
                            self.increase_level()
                        self.spawn_collision_ellipse(self.char.pos, self.collision_ellipse_img)
                        self.spawn_collision_comic(self.char.pos, self.comic_img)

                # Check if obstacle is off the screen
                if pos_y + obstacle.size[1] < 0:
                    self.reset_obstacle()

                self.health_counter = self.health_counter
                if self.collides_with_world(obstacle):
                    self.collision_count += 1
                    self.health_counter -= 50
                    self.health_txt = "HEALTH: " + str(self.health_counter) + "%"

                    if self.health_counter == 0 and not self.state_game_over:
                        self.state_game_over = True
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.menu_widget.opacity = 1
                        self.show_pause_button = False
                        self.menu_title = "GAME OVER"
                        self.menu_button = "RESTART"
                        self.highscore_txt = "HIGHSCORE: " + str(self.high_score)
                        if self.enable_music:
                            self.sound_music.stop()
                        self.game_over()

                    self.reset_obstacle()

    def collides_with_char(self, obstacle):
        '''
        Collision logic between user and obstacle
        '''
        char_left = self.char.pos[0]
        char_right = self.char.pos[0] + self.char.size[0]
        char_bottom = self.char.pos[1]
        char_top = self.char.pos[1] + self.char.size[1]

        obs_left = obstacle.pos[0]
        obs_right = obstacle.pos[0] + obstacle.size[0]
        obs_bottom = obstacle.pos[1]
        obs_top = obstacle.pos[1] + obstacle.size[1]

        # Check for collision
        if (
            char_right > obs_left
            and char_left < obs_right
            and char_top > obs_bottom
            and char_bottom < obs_top
        ):
            return True
        return False

    def collides_with_world(self, obstacle):
        '''
        collision logic between world and obstacle
        '''
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
            self.spawn_collision_circle(obstacle.pos, self.collision_circle_img)
            return True
        return False

    def reset_obstacle(self):
        '''
        Logic for obstacle spawn after collision with user or world
        '''
        obstacle_image = random.choice(self.obs_images)
        obstacle_texture = Image(source=obstacle_image).texture

        obstacle = self.obs[0]
        obstacle.texture = obstacle_texture
        if obstacle_image == "images/meteor_main.png":
            obstacle.size = (0.3 * self.width, 0.24 * self.width)
        elif obstacle_image == "images/missile_main.png":
            obstacle.size = (0.2 * self.width, 0.15 * self.width)
        elif obstacle_image == "images/dragon.png":
            obstacle.size = (0.13 * self.width, 0.13 * self.width)
        elif obstacle_image == "images/burger.png":
            obstacle.size = (0.12 * self.width, 0.1 * self.width)
        obstacle.pos = (
            random.randint(0, int(self.width) - int(obstacle.size[0])),
            int(self.height),
        )

    def on_menu_button_press(self):
        # Menu Controls
        self.reset_game()
        if self.enable_music and not self.mute_music:
            self.sound_music.play()
        self.state_game_start = True
        self.menu_widget.opacity = 0
        self.show_pause_button = True
    
    def on_pause_button_press(self):
        if not self.state_game_pause:
            self.state_game_pause = True
            self.pause_txt = "PAUSED"
            self.extras_widget.opacity = 1
        else:
            self.state_game_pause = False
            self.pause_txt = ""
            self.extras_widget.opacity = 0
    
    def on_music_button_press(self):
        if not self.mute_music:
            self.mute_music = True
            self.sound_music.stop()
            self.music_img = "images/mute_music.png"
            self.music_txt = "MUSIC: OFF"
        else:
            self.mute_music = False
            self.sound_music.play()
            self.music_img = "images/music.png"
            self.music_txt = "MUSIC: ON"

    def on_vfx_button_press(self):
        if self.vfx_option:
            self.vfx_option = False
            self.vfx_text = "VFX: OFF"
        else:
            self.vfx_option = True
            self.vfx_text = "VFX: ON"


    def spawn_collision_circle(self, position, image_file=None):

        if self.vfx_option:
            if image_file is None:
                circle_image = Image(source='images/ex.png')
            else:
                circle_image = Image(source=image_file)
            circle_image.size_hint = (None, None)
            circle_image.size = (self.collision_circle_size * self.height, self.collision_circle_size * self.height)

            scatter = Scatter(
                size_hint=(None, None),
                size=circle_image.size,
                do_translation=False
            )

            scatter.add_widget(circle_image)
            self.collision_circles.append(scatter)
            self.add_widget(scatter)

            offset_x = circle_image.width / 2
            offset_y = self.height * 0.05

            scatter.pos = (position[0] - offset_x, position[1] - offset_y)

            if self.health_counter < 51:
                time_skip = 0.05
            else:
                time_skip = 1.0

            Clock.schedule_once(lambda dt: self.remove_collision_circle(scatter), time_skip)
        else:
            pass


    def remove_collision_circle(self, circle):
        self.remove_widget(circle)
        self.collision_circles.remove(circle)


    def spawn_collision_ellipse(self, position, image_file=None):
            if self.vfx_option:
                if image_file is None:
                    image_temp = "images/light.png"
                else:
                    image_temp = image_file
                opacity = 0.6
                ellipse_image = Image(source=image_temp, opacity=0.6)
                ellipse_image.size_hint = (None, None)
                ellipse_image.size = (self.collision_ellipse_width * self.height, self.collision_ellipse_height * self.height)

                scatter = Scatter(
                    size_hint=(None, None),
                    size=ellipse_image.size,
                    do_translation=False
                )

                scatter.add_widget(ellipse_image)
                self.collision_ellipses.append(scatter)
                self.add_widget(scatter)

                offset_x = self.width * 0.09
                offset_y = self.height * 0.065

                scatter.pos = (position[0] - offset_x, position[1] - offset_y)

                Clock.schedule_once(lambda dt: self.remove_collision_ellipse(scatter), 0.5)
            else:
                pass


    def remove_collision_ellipse(self, ellipse):
        self.remove_widget(ellipse)
        self.collision_ellipses.remove(ellipse)

        
    def spawn_collision_comic(self, position, image_file=None):
        if self.vfx_option:
            if image_file is None:
                image_temp = "images/pow.png"
            else:
                image_temp = image_file
            opacity = 0.6
            comic_image = Image(source=image_temp, opacity=0.6)
            comic_image.size_hint = (None, None)
            comic_image.size = (self.collision_comic_size * self.height, self.collision_comic_size * self.height)

            scatter = Scatter(
                size_hint=(None, None),
                size=comic_image.size,
                do_translation=False
            )

            scatter.add_widget(comic_image)
            self.collision_comic.append(scatter)
            self.add_widget(scatter)

            offset_side = 0
            if position[0] > self.width/2:
                offset_side = 1
            else:
                offset_side = -2

            offset_x = self.width * 0.09 * offset_side
            offset_y = self.height * 0.04

            scatter.pos = (position[0] - offset_x, position[1] + offset_y)


            Clock.schedule_once(lambda dt: self.remove_collision_comic(scatter), 0.6)
        else:
            pass


    def remove_collision_comic(self, comic):
        self.remove_widget(comic)
        self.collision_comic.remove(comic)


class PlatformApp(App):
    from kivy.logger import Logger


    title = "WORLD DEFENDER"

    def build(self):
        return super().build()


if __name__ in ('__android__', '__main__'):
    PlatformApp().run()
