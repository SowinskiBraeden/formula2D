#!/usr/bin/env python3.11
import pygame
from models import Car, Background, Track
from util import load_image, limit

class Window:
  def __init__(self, caption, size):
    self.caption = caption
    self.size = size
    self.background = Background('track.jpg', [0, 0], size)
    self.running = False

    self._init_pygame()
    self.screen = pygame.display.set_mode((self.size))
    self.clock = pygame.time.Clock()

    self.track = Track('track_mask.png', [0, 0], size)
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

    a = 5 / (abs(self.car.speed) + 1)
    if self.car.speed == 0: a = 0
    a = limit(a, 0, 3.5)

    if pressed[pygame.K_LEFT] and round(self.car.speed, 2) > 0.55: self.car.angle += a
    if pressed[pygame.K_RIGHT] and round(self.car.speed, 2) > 0.55: self.car.angle -= a

  def _process_game_logic(self):
    self.car.update()
    self.track.detectCar(self.car)

  def _draw(self):
    self.screen.fill((0, 0, 0))
    # self.background.draw(self.screen)
    self.screen.blit(self.track.mask_image, (0, 0))
    self.screen.blit(self.car.mask_image, self.car.mask_rect)
    self.car.draw(self.screen)
    pygame.display.flip()
    self.clock.tick(60)
