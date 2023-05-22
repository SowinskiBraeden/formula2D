#!/usr/bin/env python3.11
import pygame
from models import Car
from util import load_image

class Background(pygame.sprite.Sprite):
  def __init__(self, filename, location, size):
    super().__init__()
    self.image = load_image(filename)
    self.image = pygame.transform.scale(self.image, size)
    self.rect = self.image.get_rect()
    self.rect.left, self.rect.top = location
  
  def draw(self, window):
    window.blit(self.image, self.rect)

class Window:
  def __init__(self, caption, size):
    self.caption = caption
    self.size = size
    self.background = Background('track.jpg', [0, 0], size)
    self.running = False

    self._init_pygame()
    self.screen = pygame.display.set_mode((self.size))
    self.clock = pygame.time.Clock()

    self.car = Car(880, 300)

  def main_loop(self):
    self.running = True
    while self.running:
      self._handle_input()
      self._process_game_logic()
      self._draw()

  def _init_pygame(self):
    pygame.init()
    pygame.display.set_caption(self.caption)

  def _handle_input(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (
        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
      ):
        quit()

    pressed = pygame.key.get_pressed()
    self.car.speed *= 0.95
    if pressed[pygame.K_UP]: self.car.speed += 0.2
    if pressed[pygame.K_DOWN]: self.car.speed -= 0.2
    if round(self.car.speed, 1) == 0.1: self.car.speed = 0

    c = 5
    a = c / (self.car.speed + 1)
    if self.car.speed == 0: a = 0

    if pressed[pygame.K_LEFT]: self.car.angle += a
    if pressed[pygame.K_RIGHT]: self.car.angle -= a

  def _process_game_logic(self):
    self.car.update()

  def _draw(self):
    self.screen.fill((0, 0, 0))
    self.background.draw(self.screen)
    self.car.draw(self.screen)
    pygame.display.flip()
    self.clock.tick(60)
