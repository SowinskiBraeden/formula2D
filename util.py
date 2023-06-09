#!/usr/bin/env python3.11
from pygame.image import load
from pygame import Surface
from dataclasses import dataclass
import os

@dataclass
class Colors:
  White:  tuple = (255, 255, 255)
  Green:  tuple = (0, 255, 0)
  Yellow: tuple = (230, 193, 32)
  Black:  tuple = (0, 0, 0)
  Gray:   tuple = (50, 50, 50)
  Red:    tuple = (199, 54, 54)
  Purple: tuple = (150, 15, 252)

colors = Colors()

def load_image(filename: str) -> Surface:
  if '.' in filename and filename.split('.')[1] not in ['png', 'jpg', 'jpeg']:
    raise Exception(f'Invalid filename: must be of filetype \'.png\' \'.jpg\' or \'.jpeg\' not of .{filename.split(".")[1]}')
  
  cwd = os.getcwd()
  dirName = '' if cwd.endswith('formula2D') else '/formula2D'
  path = f'{cwd}{dirName}/resources/{filename}'
  
  if not os.path.isfile(path):
    raise Exception(f'Filepath not found: \'{path}\' cannot be found')

  return load(path)

def limit(num, minimum=1, maximum=255): return max(min(num, maximum), minimum)
