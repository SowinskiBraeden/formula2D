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
    self.font_size = 20
    self.font = pygame.font.Font('freesansbold.ttf', self.font_size)
    self.screen = pygame.display.set_mode((self.size))
    self.clock = pygame.time.Clock()

    self.track = Track('track_mask.png', [0, 0], size)
    self.car = Car(880, 300)

    self.sectors = {i: Track(f'sector_{i}.png', [0,0], size) for i in range(1, 4)}
    self.last_sector = 3
    self.sector = 3

    self.lastLap = 0
    self.fastestLap = 0
    self.current = 0
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
    # Handles live lap time update
    if self.startTime != None: self.current = round(time.time() - self.startTime, 3)

    # Detect last sector and check for diff in sector
    prev_sector = self.sector

    # Handles live sector time update
    if self.startTime != None and prev_sector == self.sector:
      self.sector_times[self.sector] = round(time.time() - self.sectorStart, 3)

    for i in range(1, 4): self.sector = i if self.sectors[i].detectCar(self.car) else self.sector
    self.last_sector = prev_sector if prev_sector != self.sector else self.last_sector

    # Detect off track limits
    self.car.update()
    onTrack = self.track.detectCar(self.car)
    if not onTrack:
      self.lapTimeValid = False

    # Detect cutting track
    if self.sector != prev_sector:
      if (self.last_sector == 1 and self.sector == 3) or (self.last_sector == 2 and self.sector == 1): self.lapTimeValid = False

    # Handle complete lap (sector 3 to sector 1)
    if self.sector == 1 and self.last_sector == 3 and self.startTime != None and prev_sector != self.sector:
      self.sectorEnd = time.time()
      self.startTime = self.sectorEnd
      self.sector_times[self.last_sector] = round(self.sectorEnd - self.sectorStart, 3)
      self.sectorStart = self.sectorEnd
      self.lapTime = round(sum(self.sector_times[i] for i in range(1, 4)), 3)
      self.lastLap = self.lapTime
      fastest: bool = (self.lapTime <= self.fastestLap or self.fastestLap == 0) and self.lapTimeValid
      self.fastestLap = self.lapTime if fastest else self.fastestLap
      self.fastest_sector_times = {i: self.sector_times[i] for i in range(1, 4)} if fastest else self.fastest_sector_times
      self.lapTimeValid = True

    # Handle sector 1 to sector 2
    if self.sector == 2 and self.last_sector == 1 and prev_sector != self.sector: 
      self.sectorEnd = time.time()
      self.sector_times[self.last_sector] = round(self.sectorEnd - self.sectorStart, 3)
      self.sectorStart = self.sectorEnd
     
    # Handle sector 2 to sector 3
    if self.sector == 3 and self.last_sector == 2 and prev_sector != self.sector:
      self.sectorEnd = time.time()
      self.sector_times[self.last_sector] = round(self.sectorEnd - self.sectorStart, 3)
      self.sectorStart = self.sectorEnd
     
    # Handle initial race start (start in sector 3 move to sector 1)
    if self.sector == 1 and self.last_sector == 3 and self.startTime == None:
      self.startTime = time.time()
      self.sectorStart = self.startTime

  def _draw_laptime_data(self) -> None:

    infographic_width = 0

    # Handle sector times infographic (left)
    for i in range(1, 4):
      faster: bool = self.sector_times[i] <= self.fastest_sector_times[i]

      # Title
      title = self.font.render(f"  Sector {i}{'  |' if i != 3 else '   '}", True, colors.White, colors.Gray)
      titleRect = title.get_rect()
      titleRect.center = (titleRect.center[0] + (i-1) * titleRect.width, titleRect.center[1])
      infographic_width += titleRect.width
      self.screen.blit(title, titleRect)
      
      # Handles current sector time infographic
      overflow = 8 if i != 3 else 5 # Overflow whitespace to ensure no background seeps through if len of text is too short
      color:  tuple(int, int, int) = colors.Green if self.sector_times[i] <= self.fastest_sector_times[i] else colors.Yellow
      datac = self.font.render(f"    {self.sector_times[i]:.3f}{' '*overflow}", True, color, colors.Gray)
      dataCRect = datac.get_rect()
      dataCRect.width = titleRect.width
      dataCRect.center = (dataCRect.center[0] + (i-1) * titleRect.width, dataCRect.center[1] + self.font_size)
      self.screen.blit(datac, dataCRect)

      # Handles time diff infographic

      # Calculate time diff per sector
      diff = f"{'- ' if faster else '+'}{abs(self.fastest_sector_times[i]-self.sector_times[i]):.3f}"
      overflow = 8 if i != 3 else 5 # Overflow whitespace to ensure no background seeps through if len of text is too short
      color:  tuple(int, int, int) = colors.Green if faster else colors.Yellow
      dataD = self.font.render(f"  {diff}{' '*overflow}", True, color, colors.Gray)
      dataDRect = dataD.get_rect()
      dataDRect.width = titleRect.width
      dataDRect.center = (dataDRect.center[0] + (i-1) * titleRect.width, dataDRect.center[1] + self.font_size * 2)
      self.screen.blit(dataD, dataDRect)

      # Handles fastest sector infographic
      overflow = 8 if i != 3 else 5 # Overflow whitespace to ensure no background seeps through if len of text is too short
      sectorRecord = f"{self.fastest_sector_times[i]:.3f}"
      dataF = self.font.render(f"    {'        ' if self.fastest_sector_times[i] == 0 else sectorRecord}{' '*overflow}", True, colors.Purple, colors.Gray)
      dataFRect = dataF.get_rect()
      dataFRect.width = titleRect.width
      dataFRect.center = (dataFRect.center[0] + (i-1) * titleRect.width, dataFRect.center[1] + self.font_size * 3)
      self.screen.blit(dataF, dataFRect)

    for i in range(1, 4):
      # Solid right infographic border
      border = self.font.render("  ", False, colors.Gray, colors.Gray)
      borderRect = border.get_rect()
      borderRect.topright = (infographic_width, borderRect.topright[1] + i * self.font_size)
      self.screen.blit(border, borderRect)

    # Fastest lap // Current lap // Last lap // Invalid lap time infographic (right)

    # Fastest lap
    fastest = self.font.render(f"  Fastest:    {self.fastestLap:.3f}{' '*8}", True, colors.White, colors.Gray)
    fastestRect = fastest.get_rect()
    fastestRect.topleft = (self.size[0] - 380, 0)
    self.screen.blit(fastest, fastestRect)

    # Last lap
    last = self.font.render(f"  Last Lap:  {self.lastLap:.3f}{' '*40}", True, colors.White, colors.Gray)
    lastRect = last.get_rect()
    lastRect.topleft = (self.size[0] - 380, self.font_size)
    self.screen.blit(last, lastRect)

    # Current lap
    current = self.font.render(f"    Current:  {self.current:.3f}{' '*8}", True, colors.White, colors.Gray)
    currentRect = current.get_rect()
    currentRect.topleft = (self.size[0] - 200, 0)
    self.screen.blit(current, currentRect)

    if not self.lapTimeValid:
      text = self.font.render(f'Invalid Lap Time   ', True, colors.Red, colors.Gray)
      rect = text.get_rect()
      rect.topright = (self.size[0], self.font_size)
      self.screen.blit(text, rect)

  def _draw(self) -> None:
    self.screen.fill(colors.Black)
    self.background.draw(self.screen)
    self.track.draw(self.screen)
    self.car.draw(self.screen)
    self._draw_laptime_data()

    pygame.display.flip()
    self.clock.tick(60)
