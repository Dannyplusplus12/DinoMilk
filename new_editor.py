import pygame

import sys, os
import json


AUTO_TILE_MAP = {
	tuple(sorted([(1, 0), (0, 1)])): 0,
	tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
	tuple(sorted([(-1, 0), (0, 1)])): 2,
	tuple(sorted([(0, -1), (0, 1), (1, 0)])): 3,
	tuple(sorted([(-1, 0), (1, 0), (0, -1), (0, 1)])): 4,
	tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 5,
	tuple(sorted([(0, -1), (1, 0)])): 6,
	tuple(sorted([(-1, 0), (1, 0), (0, -1)])): 7,
	tuple(sorted([(-1, 0), (0, -1)])): 8,
}

