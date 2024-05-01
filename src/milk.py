import pygame

class Milk:
	def __init__(self, game, index, mtype=0, pos=(0, 0)):
		self.game = game
		self.index = index
		self.pos = pos
		self.img = self.game.assets['milk'][0]
		self.pos = pos
		self.status = mtype


		self.gravity = 2
		self.direction = [0, 0]

		self.anim_offsets = [[4, 5], [4, 5], [4, 4], [4, 5], [4, 5], [4, 4]]

	def rect(self):
		return pygame.Rect(self.pos[0], self.pos[1], 16, 16)

	def update(self):


		if(self.status == 1):
			last_rect = self.rect()
			rect = self.rect()
			self.direction[1] += self.gravity
			rect.y += self.direction[1]

			hitboxs = self.game.map.hitboxs_around(self.pos, (16, 16)) + self.game.milks.milks_around(self.pos, (16, 16))
			for hitbox in hitboxs:
				hitbox_r = pygame.rect.Rect(hitbox['pos'][0]*self.game.tile_size, hitbox['pos'][1]*self.game.tile_size, 16, 16)
				if(self.direction[1] > 0):
					if(rect.colliderect(hitbox_r)):
						if(not last_rect.colliderect(hitbox_r)):
							rect.bottom = hitbox_r.top

			self.pos = (rect.x, rect.y)

			self.direction[1] = 0
		elif(self.status == 0):
			player_rect = self.game.player.rect()
			player_offset = self.game.player.get_offset()
			self.pos = (player_rect.left + player_offset[0], player_rect.top - (self.index + 1) * self.img.get_height() + player_offset[1] -1)


		if(self.rect().y > 600 and self.status == 1):
			self.status = 0
			self.game.milks.re_index()


	def render(self, surf, pos, offset=(0, 0)):
		anim_offset = self.anim_offsets[self.game.player.anim_index() - 1]
		if(self.status == 1):
			render_pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
			surf.blit(self.img, render_pos)
		elif(self.status == 0):
			render_pos = (pos[0] + self.pos[0] - offset[0] - anim_offset[0], pos[1] + self.pos[1] - offset[1] - anim_offset[1] - 1)
			surf.blit(self.img, render_pos)
			

class Milks:
	def __init__(self, game, count=1):
		self.game = game
		self.count = count
		self.milks = []

		for i in range(count):
			self.milks.append(Milk(self.game, i))

	def milks_around(self, pos, size):
		rects = []
		entity_rect = pygame.rect.Rect(pos, size)

		for milk in self.milks:
			if(milk.status == 1):
				rects.append({'type': [True, False, False, False, False], 'index': 0, 'pos': [milk.rect().x // 16, milk.rect().y // 16]})

		return rects

	def get_rects(self):
		rects = []

		for milk in self.milks:
			if(milk.status == 1):
				rects.append(milk.rect())

		return rects

	def can_drop(self, pos):
		milk_r = pygame.Rect(pos[0], pos[1], 16, 16)
		hitboxs = []

		t = self.game.map.hitboxs_around(pos, (16, 16))
		for x in t:
			hitboxs.append(pygame.Rect(x['pos'][0]*16, x['pos'][1]*16, 16, 16))

		hitboxs += self.get_rects()

		for hitbox in hitboxs:
			if(milk_r.colliderect(hitbox)):
				return False

		return True

	def re_index(self):
		index = 0
		for milk in self.milks:
			if(milk.status == 0):
				milk.index = index
				index += 1

	def update(self):
		if(self.game.mouse_input[0]):
			self.re_index()

			last_milk = -1
			milk_i = -1
			for i, milk in enumerate(self.milks):
				if(milk.index > milk_i and milk.status == 0):
					milk_i = milk.index
					last_milk = i

			if(last_milk != -1 and self.can_drop(self.game.hover_tile_pos)):
				self.milks[last_milk].status = 1
				self.milks[last_milk].pos = self.game.hover_tile_pos

			self.game.mouse_input[0] = False

		rect = pygame.Rect(self.game.hover_tile_pos[0], self.game.hover_tile_pos[1], 16, 16)
		if(self.game.mouse_input[2]):
			for milk in self.milks:
				if(milk.status == 1):
					if(rect.colliderect(milk.rect())):
						milk.status = 0
			self.re_index()

			self.game.mouse_input[2] = False


		for milk in self.milks:
			milk.update()

	def render(self, surf, pos, offset=(0, 0)):
		milks = self.milks.copy()
		milks = milks[::-1]
		for milk in milks:
			milk.render(surf, pos, offset = offset)
