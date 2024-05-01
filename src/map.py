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

		self.dinos = []
		for info in map_data['special']:
			if(info['type'] == 'player'):
				self.player_pos = info['pos']
			elif(info['type'] == 'dino'):
				self.dinos.append([info['pos'], info['t_index'], info['c_index']])

		try:
			self.game.milk_count = map_data['data']['milk']
		except:
			self.game.milk_count = len(self.dinos)
			
		self.hitboxs = map_data['physic']

		self.tile_map = [map_data[x] for x in map_data if x != 'special' and x != 'physic']
		# temp = []
		# print(self.tile_map)
		# for x in self.tile_map:
		# 	temp.append({})
		# 	for y in x['grid']:
		# 		if(x['grid'][y]['type'] == 'grass'):
		# 			self.game.grasses.grasses.append(y)
		# 		else:
		# 			temp[len(temp)-1].append(x['grid'][y])
		# self.tile_map = temp


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
							# if(tile['type'] == 'grass'):
							# 	print(tile)
							surf.blit(self.game.assets[tile['type']][tile['index']], (tile['pos'][0]*self.tile_size-offset[0], tile['pos'][1]*self.tile_size-offset[1]))

			if(layer == self.main_layer):
				try:
					self.game.milks.render(surf, (0, 0), offset = offset)
					self.game.player.render(surf, offset = offset)
				except:
					pass

				for dino in self.game.dinos:
					dino.update()
					dino.render(surf, offset = offset)

