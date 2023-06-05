#!/usr/bin/env python3.11
from pygame import Rect, Surface, SRCALPHA, mask, sprite
from pygame.transform import rotate, scale
from util import load_image
import math

class Background(sprite.Sprite):
  def __init__(self, filename, location, size) -> None:
    super().__init__()
    self.image = load_image(filename)
    self.image = scale(self.image, size)
    self.rect = self.image.get_rect()
    self.rect.left, self.rect.top = location

  def draw(self, window) -> None:
    window.blit(self.image, self.rect)

class Car:
  def __init__(self, x, y) -> None:
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
    
    self.mask = mask.from_surface(self.surface)
    self.mask_image = self.mask.to_surface()
    self.mask_rect = self.mask_image.get_rect(center = self.rect.center)

    self.angle = 180
    self.speed = 0

  def update(self) -> None:
    self.x -= self.speed * math.sin(math.radians(self.angle))
    self.y -= self.speed * math.cos(math.radians(-self.angle))

  def draw(self, window) -> None:
    self.rect.topleft = (int(self.x), int(self.y))
    rotated = rotate(self.surface, self.angle)
    surface_rect = self.surface.get_rect(topleft = self.rect.topleft)
    new_rect = rotated.get_rect(center = surface_rect.center)
    window.blit(rotated, new_rect.topleft)

    self.mask = mask.from_surface(rotated)
    self.mask_image = self.mask.to_surface()
    self.mask_rect = self.mask_image.get_rect(center = surface_rect.center)

class Track:
  def __init__(self, filename, location, size) -> None:
    self.image = load_image(filename).convert_alpha()
    self.image = scale(self.image, size)
    self.rect = self.image.get_rect()
    self.rect.left, self.rect.top = location

    self.mask = mask.from_surface(self.image)
    self.mask_image = self.mask.to_surface()

  def draw(self, window) -> None:
    window.blit(self.image, self.rect)

  def detectCar(self, car: Car) -> bool:
    return self.mask.overlap(car.mask, (car.x, car.y))