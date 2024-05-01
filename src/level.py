import pygame

from src.utils import load_img, load_imgs, load_json, Animation
from src.entity import Player, Dino
from src.map import Map
from src.background import BackGrounds
from src.milk import Milks
from src.font import Font
from src.grass import GrassManner

import sys
import random, math

RENDER_SCALE = 2

class Fly:
	def __init__(self, game, pos):
		self.game = game
		self.size = (2, 2)
		self.img = pygame.Surface(self.size)
		self.img.fill((255, 140, 0))
		self.pos = pos

		self.speed_list = []

		i = -0.6
		while(i <= 0.6):
			self.speed_list.append(i)
			i += 0.2


		self.speed = (random.choice(self.speed_list), random.choice(self.speed_list))


	def rect(self):
		return pygame.Rect(self.pos, self.size)

	def update(self):

		self.pos = (self.pos[0] + self.speed[0], self.pos[1] + self.speed[1])


		change_x = random.randint(0, 240)
		if(change_x == 0):
			self.speed = (random.choice(self.speed_list), self.speed[1])

		change_y = random.randint(0, 240)
		if(change_y == 0):
			self.speed = (self.speed[0], random.choice(self.speed_list))


	def render(self, surf, offset=(0, 0)):
		surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

class Level:	
	def __init__(self, index):
		pygame.init()
		pygame.display.set_caption('DinoMilk')

		self.index = index

		self.screen = pygame.display.set_mode((800, 480))
		self.display_size = (self.screen.get_width() // RENDER_SCALE, self.screen.get_height() // RENDER_SCALE)
		self.display = pygame.Surface(self.display_size, pygame.SRCALPHA)
		self.display_2 = pygame.Surface(self.display_size)
		self.circle_radius = 20

		self.screen_shake = 0

		self.CLOCK = pygame.time.Clock()

		self.assets = {
			'background': load_imgs('background'),
			'player': load_img('player/idle/1.png'),
			'player/idle': Animation(load_imgs('player/idle'), img_dur=8),
			'player/idle/offset': load_json('assets/img/player/idle/offset.json'),
			'player/move': Animation(load_imgs('player/move'), img_dur=8),
			'player/move/offset': load_json('assets/img/player/move/offset.json'),
			'light': load_img('light.png'),
			'black': load_img('black.png'),
			'milk': load_imgs('milk'),
			'grass': load_imgs('grass'),
			'grasses': load_imgs('grasses'),
			'physic': load_imgs('physic'),
			'ground': load_imgs('ground'),
			'ground_2': load_imgs('ground_2'),
			'tree': load_imgs('tree'),
			'rock': load_imgs('rock'),
			'dino/1': Animation(load_imgs('dino/1'), img_dur=8),
			'dino/1/offset': load_json('assets/img/dino/1/offset.json'),
			'dino/2': Animation(load_imgs('dino/2'), img_dur=8),
			'dino/2/offset': load_json('assets/img/dino/2/offset.json'),
			'dino/3': Animation(load_imgs('dino/3'), img_dur=8),
			'dino/3/offset': load_json('assets/img/dino/3/offset.json'),
			'dino/4': Animation(load_imgs('dino/4'), img_dur=8),
			'dino/4/offset': load_json('assets/img/dino/4/offset.json'),

			'chatbox': load_img('chatbox.png'),
		}

 
		self.scroll = [0, 0]
		self.mouse_input = [False, False, False]
		self.arrow_input = [False, False, False, False]

		self.night = False
		self.background = BackGrounds(self.assets['background'])

		self.grasses = GrassManner(self, [])

		self.map = Map(self)
		self.map.update()
		self.map.load('map/' + str(self.index) + '.json')
		self.tile_size = 16

		self.in_conver = False
		self.conver_avt = pygame.Surface((0, 0))
		self.c_index = 0
		self.c_continue = False
		self.player = Player(self, self.map.player_pos)
		self.player_size = (self.player.rect().width, self.player.rect().height)

		self.milks = Milks(self, self.milk_count)

		self.dinos = []
		for info in self.map.dinos:
			self.dinos.append(Dino(self, info[0], info[1], info[2]))

		self.flies = []
		for i in range(50):
			self.flies.append(Fly(self, (random.randint(-1000, 1000), random.randint(-200, 600))))

		self.font = Font()

		self.break_timer = 0
		self.start_timer = 180



	def light(self, size, yellow=False):
		light = self.assets['light'].copy()
		img = self.assets['light'].copy()
		if(yellow):
			img.fill((255, 255, 35))
			img.blit(light, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
		return pygame.transform.scale(img, size)


	def run(self):
		while True:
			self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
			self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
			render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
			
			mouse_pos = pygame.mouse.get_pos()
			self.mouse_pos = (mouse_pos[0] / RENDER_SCALE, mouse_pos[1] / RENDER_SCALE)
			self.mouse_rect = pygame.Rect(mouse_pos, (1, 1))
			self.hover_tile_pos = ((self.mouse_pos[0] + render_scroll[0]) // self.tile_size * self.tile_size, (self.mouse_pos[1] + render_scroll[1]) // self.tile_size * self.tile_size)


			self.screen.fill((0, 0, 0, 0))
			self.display.fill((0, 0, 0, 0))
			self.display_2.fill((0, 0, 0, 0))
			self.background.render(self.display_2)
			
			if(self.start_timer == 0):
				self.player.update()
			

			self.milks.update()

			self.map.update()
			self.map.render(self.display, offset = render_scroll)
			

			# outline
			display_mask = pygame.mask.from_surface(self.display)
			display_shadow = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(255, 0, 0, 0))
			for offset in [(-2, 0), (0, -2), (2, 0), (0, 2)]:
				self.display_2.blit(display_shadow, offset)
			self.display_2.blit(self.display, (0, 0))
			# 


			select_pos = (self.hover_tile_pos[0] - self.scroll[0], self.hover_tile_pos[1] - self.scroll[1])
			select_rect = pygame.rect.Rect(select_pos[0], select_pos[1], self.tile_size, self.tile_size)
			pygame.draw.rect(self.display_2, (180, 0, 0, 180), select_rect)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						pygame.quit() 
						sys.exit()

					if(self.in_conver):
						self.c_continue = True

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

				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button < 4:
						self.mouse_input[event.button - 1] = True

				if event.type == pygame.MOUSEBUTTONUP:
					if event.button < 4:
						self.mouse_input[event.button - 1] = False


			if(self.night):

				light_surface = pygame.Surface(self.display_size)
				light_surface.fill((12, 10, 18))

				player_center = self.player.rect().center
				player_light = self.light((140, 140))
				player_light_pos = (player_center[0] - player_light.get_width() / 2 - self.scroll[0], player_center[1] - player_light.get_height() / 2 - self.scroll[1])

				light_surface.blit(player_light, player_light_pos, special_flags=pygame.BLEND_RGBA_ADD)


				for milk in self.milks.milks:
					if(milk.status == 0):
						continue

					light = self.light((50, 50))
					light_center = milk.rect().center
					light_pos = (light_center[0] - light.get_width() / 2 - self.scroll[0], light_center[1] - light.get_height() / 2 - self.scroll[1])

					light_surface.blit(light, light_pos, special_flags=pygame.BLEND_RGBA_ADD)


				
				for fly in self.flies:

					if(fly.pos[0] > self.scroll[0] - 50 and fly.pos[0] < self.scroll[0] + self.display_size[0] + 50):
						if(fly.pos[1] > self.scroll[1] - 50 and fly.pos[1] < self.scroll[1] + self.display_size[1] + 50):

							fly.update()
							fly.render(self.display_2, offset=self.scroll)

							light = self.light((46, 46), yellow=True)
							light_center = fly.rect().center
							light_pos = (light_center[0] - light.get_width() / 2 - self.scroll[0], light_center[1] - light.get_height() / 2 - self.scroll[1])

							light_surface.blit(light, light_pos, special_flags=pygame.BLEND_RGBA_ADD)

				
				self.display_2.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
			
			if(self.in_conver):

				chat_box = pygame.Surface((300, 50))
				chat_box.set_colorkey((0, 0, 0))
				chat_box.blit(self.assets['chatbox'], (0, 0))

				text_surf = pygame.Surface((240, 40))
				text_surf.set_colorkey((0, 0, 0))

				c_data = self.conversation[self.c_index]

				self.font.render(text_surf, c_data[1], color=(25, 32, 17))
				chat_box.blit(text_surf, (10, 5))
				
				if(c_data[0] == '0'):
					self.display_2.blit(chat_box, (5, 160))
				else:
					self.display_2.blit(chat_box, (95, 160))

				if(self.c_continue):
					self.c_index += 1
					self.c_continue = False
				if(self.c_index == len(self.conversation)):
					self.c_index = 0
					self.in_conver = False

				conver_avt_1 = self.player.img
				conver_avt_2 = self.conver_avt
				avt_size = conver_avt_2.get_size()
				avt_size = (avt_size[0]*4, avt_size[1]*4)
				self.display_2.blit(pygame.transform.scale(conver_avt_1, avt_size), (0, self.display_size[1] - avt_size[1] / 2))
				self.display_2.blit(pygame.transform.scale(pygame.transform.flip(conver_avt_2, True, False), avt_size), (self.display_size[0] - avt_size[0], self.display_size[1] - avt_size[1] / 2))



			if(len([x for x in self.milks.milks if x.status == 0 or x.status == 1]) == 0 and not self.in_conver):
				if(self.break_timer == 0):
					self.break_timer = 120
			if(self.break_timer):
				self.break_timer = self.break_timer - 1

				mask = pygame.Surface(self.display_size)
				mask.fill((0, 0, 0))
				mask.set_colorkey((255, 255, 255))
				player_center = self.player.rect().center	
				pygame.draw.circle(mask, (255, 255, 255), (player_center[0]-self.scroll[0], player_center[1]-self.scroll[1]), self.circle_radius)

				self.circle_radius = self.circle_radius - 2

				self.display_2.blit(mask, (0, 0))

			if(self.break_timer == 1):
				break

			if(self.start_timer > 0):
				lazer_beam_len = ((self.start_timer)*-4 + 500)
				lazer_beam_start = [self.player.rect().center[0] - self.scroll[0], self.player.rect().center[1] - 240 - self.scroll[1]]
				lazer_beam_end = [lazer_beam_start[0], min(lazer_beam_start[1] + lazer_beam_len + 28, lazer_beam_start[1] + 264)]
				pygame.draw.line(self.display_2, (255, 255, 255), lazer_beam_start, lazer_beam_end, 64)
				self.start_timer -= 1

				mask = pygame.Surface(self.display_size)
				mask.fill((0, 0, 0))
				mask.set_colorkey((255, 255, 255))
				player_center = self.player.rect().center	
				pygame.draw.circle(mask, (255, 255, 255), (player_center[0]-self.scroll[0], player_center[1]-self.scroll[1]), self.circle_radius)

				self.circle_radius = self.circle_radius + 2

				if(self.start_timer == 0):
					self.circle_radius = self.display_size[0] / 2

				self.display_2.blit(mask, (0, 0))

			self.screen_shake = max(0, self.screen_shake-1)
			screen_shake_offset = (random.random() * self.screen_shake + self.screen_shake / 2, random.random() * self.screen_shake + self.screen_shake / 2)
			self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (screen_shake_offset[0], screen_shake_offset[1]))
	
			self.CLOCK.tick(60)
			pygame.display.update()