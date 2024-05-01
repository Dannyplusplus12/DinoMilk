import pygame
import math, random


from src.utils import load_imgs

class Grass:
	def __init__(self, pos, img):
		self.pos = pos
		self.img = img

		self.loc = (int(self.pos[0]/16), int(self.pos[1]/16))
		self.rotate = 0

	def rect(self):
		return pygame.Rect(self.pos, self.img.get_size())

	def center(self):
		center = self.rect().center
		center = (center[0], center[1] - 8)
		return center 

	def update(self, e_pos):
		if self.rotate < 0:
			self.rotate += 2
		if self.rotate > 0:
			self.rotate -= 2

		center = self.center()
		if abs(e_pos[1] - center[1]) > 16:
			return

		dis = abs(center[0] - e_pos[0])
		if dis > 16:
			return

		self.rotate = (-dis+16)*6
		if e_pos[0] < center[0]:
			self.rotate *= -1

	def render(self, surf):
		img = pygame.transform.rotate(self.img, self.rotate)
		size = img.get_size()
		pos = (int(self.pos[0] - abs(size[0] - 32) / 2), int(self.pos[1] - abs(size[1] - 32) / 2))
		surf.blit(img, pos)

class GrassManner:
	def __init__(self, game, data):
		self.game = game
		self.data = data

		self.imgs = load_imgs('grass')

		self.grasses = []

		for pos in self.data:
			for i in range(1, 16, 2):
				img_i = random.choice([0, 0, 0, 1, 1, 1, 2, 3, 3, 3, 4])
				img = self.imgs[img_i]
				self.grasses.append(Grass((pos[0]-16+i, pos[1]), img))


	def update(self):
		e_pos = self.game.player.center()

		for grass in self.grasses:
			grass.update(e_pos)


	def render(self, surf):
		for grass in self.grasses:
			grass.render(surf)
