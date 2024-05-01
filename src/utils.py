import pygame
import os, json

BASE_IMG_PATH = 'assets/img/'
BASE_FONT_PATH = 'assets/font/'

def load_img(path):
	img = pygame.image.load(BASE_IMG_PATH + path).convert()
	img.set_colorkey((0, 0, 0))

	return img


def load_imgs(path):
	imgs = []
	for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
		try:
			imgs.append(load_img(path + '/' + img_name))
		except:
			pass

	return imgs

def load_font(path):
	img = pygame.image.load(BASE_FONT_PATH + path).convert()
	img.set_colorkey((0, 0, 0))

	return img

def load_json(path):
	f = open(path, 'r')
	data = json.load(f)
	f.close()

	return data

def clip(surf, rect):
    if type(rect) == tuple:
        rect = pygame.Rect(*rect)
    surf.set_clip(rect)
    image = surf.subsurface(surf.get_clip()).copy()
    surf.set_clip(None)
    return image

def replace_color(surf, first_color, last_color):
	color_key = surf.get_colorkey()
	mask = surf.copy()
	mask.set_colorkey(first_color)
	
	img = pygame.Surface(surf.get_size())
	img.fill(last_color)
	img.blit(mask, (0, 0))
	img.set_colorkey(color_key)

	return img

class Animation:
	def __init__(self, imgs, img_dur=5, loop=True):
		self.imgs = imgs
		self.img_dur = img_dur
		self.loop = loop
		self.done = False
		self.frame = 0

	def copy(self):
		return Animation(self.imgs, self.img_dur, self.loop)

	def update(self):
		if self.loop:
			self.frame = (self.frame+1) % (self.img_dur * len(self.imgs))
		else:
			self.frame = min(self.frame+1) % (self.img_dur * len(self.ings) - 1)
			if(self.frame >= self.img_dur * len(self.imgs) - 1):
				self.done = True

	def img(self):
		return self.imgs[int(self.frame / self.img_dur)]