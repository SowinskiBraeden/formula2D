#!/usr/bin/env python3.11
import pygame
from models import Car, Background, Track
from util import load_image, limit, colors
import time

class Window:
  def __init__(self, caption, size) -> None:
    self.caption = caption
    self.size = size
    self.background = Background('track.jpg', [0, 0], size)
    self.running = False

    self._init_pygame()
    self.font = pygame.font.Font('freesansbold.ttf', 24)
    self.screen = pygame.display.set_mode((self.size))
    self.clock = pygame.time.Clock()

    self.track = Track('track_mask.png', [0, 0], size)
    self.car = Car(880, 300)

    self.sectors = {i: Track(f'sector_{i}.png', [0,0], size) for i in range(1, 4)}
    self.last_sector = 3
    self.sector = 3

    self.lastLap = 0
    self.fastestLap = 0
    self.startTime = None
    self.sectorStart = None
    self.sectorEnd = None
    self.fastest_sector_times = {i: 0 for i in range(1, 4)}
    self.sector_times = {i: 0 for i in range(1, 4)}
    self.lapTime = 0
    self.lapTimeValid = True

  def main_loop(self) -> None:
    self.running = True
    while self.running:
      self._handle_input()
      self._process_game_logic()
      self._draw()

  def _init_pygame(self) -> None:
    pygame.init()
    pygame.display.set_caption(self.caption)

  def _handle_input(self) -> None:
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

  def _process_game_logic(self) -> None:
    t = time.time()
    # if self.startTime != None: print(round(t - self.startTime, 3))

    self.car.update()
    onTrack = self.track.detectCar(self.car)
    if not onTrack:
      self.lapTimeValid = False

    prev_sector = self.sector
    for i in range(1, 4): self.sector = i if self.sectors[i].detectCar(self.car) else self.sector
    self.last_sector = prev_sector if prev_sector != self.sector else self.last_sector

    if self.sector != prev_sector:
      if (self.last_sector == 1 and self.sector == 3) or (self.last_sector == 2 and self.sector == 1): self.lapTimeValid = False

    if self.sector == 1 and self.last_sector == 3 and self.startTime != None and prev_sector != self.sector:
      self.sectorEnd = time.time()
      self.startTime = self.sectorEnd
      self.sector_times[self.last_sector] = round(self.sectorEnd - self.sectorStart, 3)
      self.sectorStart = self.sectorEnd
      self.lapTime = round(sum(self.sector_times[i] for i in range(1, 4)), 3)
      fastest: bool = (self.lapTime <= self.fastestLap or self.fastestLap == 0) and self.lapTimeValid
      self.fastestLap = self.lapTime if fastest else self.fastestLap
      self.fastest_sector_times = {i: self.sector_times[i] for i in range(1, 4)} if fastest else self.fastest_sector_times
      self.lapTimeValid = True

    if self.sector == 2 and self.last_sector == 1 and prev_sector != self.sector: 
      self.sectorEnd = time.time()
      self.sector_times[self.last_sector] = round(self.sectorEnd - self.sectorStart, 3)
      self.sectorStart = self.sectorEnd
     
    if self.sector == 3 and self.last_sector == 2 and prev_sector != self.sector:
      self.sectorEnd = time.time()
      self.sector_times[self.last_sector] = round(self.sectorEnd - self.sectorStart, 3)
      self.sectorStart = self.sectorEnd
     
    if self.sector == 1 and self.last_sector == 3 and self.startTime == None:
      self.startTime = time.time()
      self.sectorStart = self.startTime

  def _draw(self) -> None:
    self.screen.fill(colors.Black)
    self.background.draw(self.screen)
    self.track.draw(self.screen)
    self.car.draw(self.screen)

    for i in range(1, len(self.sector_times) + 1):
      faster = self.sector_times[i] <= self.fastest_sector_times[i]
      color = colors.Green if faster else colors.Yellow
      diff = f"{'-' if faster else '+'}{abs(self.fastest_sector_times[i]-self.sector_times[i]):.3f}"
      text = self.font.render(f"S{i}: {self.sector_times[i]:.3f} | {diff} | Fastest S{i}: {self.fastest_sector_times[i]:.3f}", True, color, colors.Black)
      textRect = text.get_rect()
      textRect.center = (textRect.center[0], textRect.center[1] + (i-1) * 24)
      self.screen.blit(text, textRect)
    text = self.font.render(f"Fastest Lap: {self.fastestLap:.3f}", True, colors.Green, colors.Black)
    rect = text.get_rect()
    rect.center = (rect.center[0], rect.center[1] + 72)
    self.screen.blit(text, rect)
    color = colors.Green if self.lapTimeValid else colors.Yellow
    text = self.font.render(f'Current Lap: {"Valid" if self.lapTimeValid else "Invalid"}', True, color, colors.Black)
    rect = text.get_rect()
    rect.center = (rect.center[0], rect.center[1] + 96)
    self.screen.blit(text, rect)

    pygame.display.flip()
    self.clock.tick(60)
