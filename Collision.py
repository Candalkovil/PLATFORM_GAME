from kivy.uix.image import Image
from kivy.properties import Clock
from kivy.uix.scatter import Scatter


def spawn_collision_circle(self, position, image_file=None):
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


def remove_collision_circle(self, circle):
    self.remove_widget(circle)
    self.collision_circles.remove(circle)


def spawn_collision_ellipse(self, position, image_file=None):
    if image_file is None:
        image_temp = "images/aura.png"
    else:
        image_temp = image_file
    opacity = 0.6
    ellipse_image = Image(source=image_temp, opacity=0.6)
    ellipse_image.size_hint = (None, None)
    ellipse_image.size = (self.collision_ellipse_size * self.height, self.collision_ellipse_size * self.height)

    scatter = Scatter(
        size_hint=(None, None),
        size=ellipse_image.size,
        do_translation=False
    )

    scatter.add_widget(ellipse_image)
    self.collision_ellipses.append(scatter)
    self.add_widget(scatter)

    offset_x = self.width * 0.01
    offset_y = self.height * 0.07

    scatter.pos = (position[0] - offset_x, position[1] - offset_y)

    Clock.schedule_once(lambda dt: self.remove_collision_ellipse(scatter), 0.5)


def remove_collision_ellipse(self, ellipse):
    self.remove_widget(ellipse)
    self.collision_ellipses.remove(ellipse)
