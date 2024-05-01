import pygame

from src.utils import load_img, load_imgs, load_json, Animation

import sys
import random, math

RENDER_SCALE = 2


import pygame

GIFT_HEIGHT = [0, 10, 16, 16, 16, 16, 14]
TOTAL_GIFT_HEIGHT = [0, 8, 22, 36, 50, 64, 72]

import json
import pygame

PHYSICS_TILES = ['ground']
PALLET_TILES = ['pallet']

class Map:
	def __init__(self, game, tile_size = 16):
		self.game = game
		self.tile_size = tile_size
		self.grid_tiles = {}
		self.hitboxs = {}
		self.offgrid_tiles = []
		self.player_pos = [0, 0]

		self.main_layer = 5

	def load(self, path):
		f = open(path, 'r')
		map_data = json.load(f)
		f.close()

		self.player_pos = map_data['special'][0]['pos']
		self.hitboxs = map_data['physic']

		self.tile_map = [map_data[x] for x in map_data if x != 'special' and x != 'physic']

	def can_place(self, pos):
		block_r = pygame.Rect(pos[0], pos[1], 16, 16)
		hitboxs = self.game.milks.milks_around(pos, (16, 16)) + self.hitboxs_around(pos, (16, 16))
		for hitbox in hitboxs:
			hitbox_r = pygame.Rect(hitbox['pos'][0]*16, hitbox['pos'][0]*16, 16, 16)
			# if(block_r.colliderect(hitbox_r)):
			if(pygame.Rect.colliderect(block_r, hitbox_r)):
				print(hitbox_r)
				return False
		return True

	def hitboxs_around(self, pos, size):
		hitboxs = []

		entity_topleft = (int(pos[0] // self.tile_size) - 2, int(pos[1] // self.tile_size) - 2)
		entity_bottomright = (int((pos[0] + size[0]) // self.tile_size) + 1, int((pos[1] + size[1]) // self.tile_size) + 1)
		for x in range(entity_topleft[0], entity_bottomright[0]+1):
			for y in range(entity_topleft[1], entity_bottomright[1]+1):
				check_loc = str(x) + '; ' + str(y)
				if(check_loc in self.hitboxs):
					hitboxs.append(self.hitboxs[check_loc])

		return hitboxs

	def update(self):
		pass

	def render(self, surf, offset=(0, 0), mode='offgrid grid special'):

		for layer in range(len(self.tile_map)):
			if('offgrid' in mode):
				for loc in self.tile_map[layer]['offgrid']:
					tile = loc
					surf.blit(self.game.assets[tile['type']][tile['index']], (tile['pos'][0]-offset[0], tile['pos'][1]-offset[1]))

			if('grid' in mode):
				for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
					for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
						loc = str(x) + '; ' + str(y)
						if(loc in self.tile_map[layer]['grid']):
							tile = self.tile_map[layer]['grid'][loc]
							surf.blit(self.game.assets[tile['type']][tile['index']], (tile['pos'][0]*self.tile_size-offset[0], tile['pos'][1]*self.tile_size-offset[1]))

			# if(layer == self.main_layer):
			# 	self.game.player.render(surf, offset = offset)




class Player:
	def __init__(self, game, pos):
		self.game = game
		self.pos = pos
		self.size = (16, 16)

		self.direction = [0, 0]
		self.speed = 2
		self.can_move = True
		self.collisions = {'left': False, 'right': False, 'top': False, 'bottom': 'False'}

		self.gravity = 0.2
		
		self.can_jump = True
		self.jump_speed = 4

		self.action = ''
		self.anim_offset = [0, 0, 0, 0]
		self.flip = False
		self.set_action('idle')

	def rect(self):
		return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

	def get_offset(self):
		return self.anim_offset

	def set_action(self, action):
		if action != self.action:
			self.action = action
			self.animation = self.game.assets['player/' + self.action].copy()
			self.anim_offsets = self.game.assets['player/' + self.action + '/offset']

	def update_by_input(self):
		if self.game.arrow_input[0]:
			self.direction[0] -= self.speed
		if self.game.arrow_input[1]:
			self.direction[0] += self.speed
		if self.game.arrow_input[2]:
			if(self.can_jump):
				self.jump()

			
	def horizontral_moverment(self):
		last_rect = self.rect()
		self.pos[0] += self.direction[0]
		entity_rect = self.rect()
		for hitbox in self.game.map.hitboxs_around(self.pos, self.size):
			hitbox_r = pygame.Rect(hitbox['pos'][0]*16, hitbox['pos'][1]*16, 16, 16)
			if(entity_rect.colliderect(hitbox_r)):
				if(self.direction[0] > 0):
					if(hitbox['type'][0] or hitbox['type'][2]):
						if(not last_rect.colliderect(hitbox_r)):
							entity_rect.right = hitbox_r.left
							self.direction[0] = 0
							self.collisions['right'] = True
				if(self.direction[0] < 0):
					if(hitbox['type'][0] or hitbox['type'][2]):
						if(not last_rect.colliderect(hitbox_r)):
							entity_rect.left = hitbox_r.right
							self.direction[0] = 0
							self.collisions['left'] = True

		self.pos[0] = entity_rect.x

		if(self.direction[0] > 0):
			self.flip = False
		if(self.direction[0] < 0):
			self.flip = True

	def vertical_moverment(self):
		self.apply_gravity()

		last_rect = self.rect()
		self.pos[1] += self.direction[1]
		entity_rect = self.rect()

		for hitbox in self.game.map.hitboxs_around(self.pos, self.size):
			hitbox_r = pygame.Rect(hitbox['pos'][0]*16, hitbox['pos'][1]*16, 16, 16)
			if(entity_rect.colliderect(hitbox_r)):
				if(self.direction[1] > 0):
					if(hitbox['type'][0] or hitbox['type'][1]):
						if(not last_rect.colliderect(hitbox_r)):
							entity_rect.bottom = hitbox_r.top
							self.can_jump = True
							self.collisions['bottom'] = True
				if(self.direction[1] < 0):
					if(hitbox['type'][0] or hitbox['type'][3]):
						if(not last_rect.colliderect(hitbox_r)):
							entity_rect.top = hitbox_r.bottom
							self.collisions['top'] = True
		if(self.collisions['bottom'] or self.collisions['top']):
			self.direction[1] = 0
		else:
			self.can_jump = False
		self.pos[1] = entity_rect.y

	def apply_gravity(self):
		self.direction[1] += self.gravity

		
	def jump(self):
		self.direction[1] -= self.jump_speed

	def update_moverment(self):
		self.update_by_input()
		self.vertical_moverment()
		self.horizontral_moverment()

	def update_animation(self):
		if(self.direction[0] == 0):
			self.set_action('idle')

		if(self.direction[0] != 0):
			self.set_action('move')

		self.anim_offset = self.game.assets['player/' + self.action + '/offset'][str(int(self.animation.frame / self.animation.img_dur) + 1)]

		self.animation.update()
		self.display = pygame.Surface((self.animation.img().get_width(), self.animation.img().get_height()))
		self.display.set_colorkey((255, 0, 0))
		self.display.fill((255, 0, 0))
		self.display.blit(self.animation.img(), (0 , (self.display.get_height() - self.animation.img().get_height())))

		self.direction[0] = 0
		self.collisions = {'left': False, 'right': False, 'top': False, 'bottom': False}

	def update(self):
		self.update_moverment()
		self.update_animation()

	def render(self, surf, offset=(0, 0)):

		surf.blit(pygame.transform.flip(self.display, self.flip, False), (self.pos[0] - offset[0]- self.anim_offset[1], self.pos[1] - 5 - offset[1]))

class Enemy:
	def __init__(self, game, pos):
		self.game = game
		self.pos = pos
		self.size = (32, 32)

		self.speed = 2
		self.direction = [0, 0]
		self.collisions = {'left': False, 'right': False, 'top': False, 'bottom': 'False'}

		self.flip = False
		self.img = pygame.Surface(self.size)
		self.img.fill((255, 0, 0))
		self.timer = 0
		
		self.target = (0, 0)
		self.at_timer = 0
		self.at_time = 60
		self.at = False

	def rect(self):
		return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

	def atack(self, pos, target):

		render_pos = (pos[0] - self.offset[0], pos[1] - self.offset[1])
		render_target = (target[0] - self.offset[0], target[1] - self.offset[1])

		if(self.at_timer < self.at_time):
			# print(render_pos, render_target)
			pygame.draw.line(self.game.display, (255, 0, 0), render_pos, render_target, self.at_timer % 5)
		if(self.at_timer == self.at_time):
			a = abs(pos[0] - target[0])
			b = abs(pos[1] - target[1])
			c = math.sqrt(a*a + b*b)

			tan_a = a / c
			tan_b = b / c

			x = 500 * tan_a
			y = 500 * tan_b

			if(pos[0] > target[0]):
				x = -x
			if(pos[1] > target[1]):
				y = -y

			x += pos[0]
			y += pos[1]

			self.target = (x, y)
			self.game.screen_shake = 8

		if(self.at_timer >= self.at_time):
			self.game.screen_shake = 4
			s = self.at_timer-60
			s = -s + 62
			pygame.draw.line(self.game.display, (255, 255, 255), render_pos, (self.target[0] - self.offset[0], self.target[1] - self.offset[1]), s)

		self.at_timer += 1
		if(self.at_timer == 120):
			self.at_timer = 0
			self.at = False

			a = abs(pos[0] - self.target[0])
			b = abs(pos[1] - self.target[1])
			c = math.sqrt(a*a + b*b)

			tan_a = a / c
			tan_b = b / c

			x = 500 * tan_a
			y = 500 * tan_b

			x = int(x)

			for i in range(50):
				px = random.randint(0, x)
				c = px / tan_a
				py = math.sqrt(c*c - px*px)
				if(pos[0] > self.target[0]):
					px = -px
				if(pos[1] > self.target[1]):
					py = -py
				px += pos[0]
				self.game.circle_particles.append([(px, py), (255, 255, 255), random.randint(2, 6), (random.randint(-1, 1), random.randint(1, 2))])


	def update(self):
		self.timer += 1
		self.direction[0] = 0
		if(not self.at_timer > self.at_time):
			self.direction[0] += self.speed
		if(self.timer % 200 == 0):
			self.speed = -self.speed

		center = self.rect().center
		target = self.game.player.rect().center

		self.offset = self.game.scroll

		if(self.timer % 300 == 0):
			self.at = True

		if(self.at):
			self.atack(center, target)

		self.pos = [self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]]

	def render(self, surf, offset=(0, 0)):

		surf.blit(pygame.transform.flip(self.img, self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))





class Level:	
	def __init__(self):
		pygame.init()

		self.screen = pygame.display.set_mode((800, 480))
		self.display_size = (self.screen.get_width() // RENDER_SCALE, self.screen.get_height() // RENDER_SCALE)
		self.display = pygame.Surface(self.display_size, pygame.SRCALPHA)

		self.screen_shake = 0

		self.CLOCK = pygame.time.Clock()

		self.assets = {
			'background': load_imgs('background'),
			'player': load_img('player/idle/1.png'),
			'player/idle': Animation(load_imgs('ni'), img_dur=8),
			'player/idle/offset': [1, 3, 1, 2],
			# 'player/move': Animation(load_imgs('player/move'), img_dur=8),
			# 'player/move/offset': load_json('player/move/offset.json'),
			'light': load_img('light.png'),
			'black': load_img('black.png'),
			'milk': load_imgs('milk'),
			'physic': load_imgs('physic'),
			'ground': load_imgs('ground'),
			'ground_2': load_imgs('ground_2'),
			'tree': load_imgs('tree'),
			'rock': load_imgs('rock'),
			'grass': load_imgs('grass'),
		}

 
		self.scroll = [0, 0]
		self.arrow_input = [False, False, False, False]

		self.map = Map(self)
		self.map.update()
		self.map.load('map/2.json')
		self.tile_size = 16

		self.player = Player(self, [0, 0])
		self.enemies = []

		self.enemies.append(Enemy(self, (-200, 0)))
		self.circle_particles = []

	def run(self):
		while True:
			self.display.fill((0, 0, 0))

			self.screen_shake = max(0, self.screen_shake - 1)

			self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
			self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1] - 48) / 30
			render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
			
			mouse_pos = pygame.mouse.get_pos()
			self.mouse_pos = (mouse_pos[0] / RENDER_SCALE, mouse_pos[1] / RENDER_SCALE)
			self.mouse_rect = pygame.Rect(mouse_pos, (1, 1))

			
			self.map.update()
			self.map.render(self.display, offset = render_scroll)
			
			self.player.update()
			self.player.render(self.display, offset = render_scroll)

			for enemy in self.enemies:
				enemy.update()
				enemy.render(self.display, offset=self.scroll)

	# self.game.circle_particles.append([(px, py), (255, 255, 255), random.randint(2, 6), (1, 1)])
			for p in self.circle_particles:
				pygame.draw.circle(self.display, p[1], (p[0][0]-self.scroll[0], p[0][1]-self.scroll[1]), p[2])
				p[0] = (p[0][0]+p[3][0], p[0][1]+p[3][1])

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						pygame.quit() 
						sys.exit()
					if event.key in [pygame.K_LEFT, pygame.K_a]:
						self.arrow_input[0] = True
					if event.key in [pygame.K_RIGHT, pygame.K_d]:
						self.arrow_input[1] = True
					if event.key in [pygame.K_UP, pygame.K_w, pygame.K_SPACE]:
						self.arrow_input[2] = True
					if event.key in [pygame.K_DOWN, pygame.K_s]:
						self.arrow_input[3] = True
						
				if event.type == pygame.KEYUP:
					if event.key in [pygame.K_LEFT, pygame.K_a]:
						self.arrow_input[0] = False
					if event.key in [pygame.K_RIGHT, pygame.K_d]:
						self.arrow_input[1] = False
					if event.key in [pygame.K_UP, pygame.K_w, pygame.K_SPACE]:
						self.arrow_input[2] = False
			
			screen_shake_offset = (random.random() * self.screen_shake + self.screen_shake / 2, random.random() * self.screen_shake + self.screen_shake / 2)
			self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (screen_shake_offset[0], screen_shake_offset[1]))

			self.CLOCK.tick(60)
			pygame.display.update()

level = Level()
level.run()