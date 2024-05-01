import pygame
import random, operator

class BackGround:
	def __init__(self, img, depth, surf_size=(420, 240), pos=(0, 0)):
		self.img = img
		self.depth = depth
		self.surf_size = surf_size
		self.pos = pos

	def update(self, offset=(0, 0)):
		self.pos = (offset[0]*self.depth*0.1, 0)

	def render(self, surf):
		surf.blit(self.img, self.pos)

class BackGrounds:
	def __init__(self, background_imgs, surf_size=(420, 240)):
		self.backgrounds = []
		self.background_imgs = background_imgs
		self.background_size = [self.background_imgs[0].get_width(), self.background_imgs[0].get_height()]
		self.surf_size = surf_size

		for layer in range(len(self.background_imgs)):
			self.backgrounds.append(BackGround(background_imgs[layer], layer))

	def update(self, offset):
		for bg in self.backgrounds:
			bg.update(offset)
			layer = bg.depth
			if(bg.pos[0] + self.background_size[0] <= self.surf_size[0] + 10):
				backgrounds.append(BackGround(background_imgs[layer]), layer, pos = bg.pos[0] + self.background_size[0] + 1)
			# if(bg.pos[0] + self.background_size[0] <= 0):
			# 	del bg
		self.backgrounds.sort(key=operator.attrgetter('depth'))

	def render(self, surf, offset=(0, 0)):
		for background in self.backgrounds:
			background.render(surf)
