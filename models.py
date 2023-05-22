#!/usr/bin/env python3.11
from pygame import Rect, Surface, SRCALPHA
from pygame.transform import rotate, scale
from util import load_image
import math, os

class Car:
  def __init__(self, x, y):
    # Load image and set to scale
    img = load_image('car.png')
    img = rotate(img, 90)
    img = scale(img, (img.get_width()/10, img.get_height()/10))

    self.width = img.get_height()
    self.height = img.get_width()
    self.x = x - self.width / 2
    self.y = y - self.height / 2
    self.rect = Rect(x, y, self.height, self.width)
    self.surface = Surface((self.height, self.width), SRCALPHA, 32).convert_alpha()
    self.surface.blit(img, (0, 0))
    self.angle = 180
    self.speed = 0

  def update(self):
    self.x -= self.speed * math.sin(math.radians(self.angle))
    self.y -= self.speed * math.cos(math.radians(-self.angle))

  def draw(self, window):
    self.rect.topleft = (int(self.x), int(self.y))
    rotated = rotate(self.surface, self.angle)
    surface_rect = self.surface.get_rect(topleft = self.rect.topleft)
    new_rect = rotated.get_rect(center = surface_rect.center)
    window.blit(rotated, new_rect.topleft)