import pygame
from src.utils import load_json

GIFT_HEIGHT = [0, 10, 16, 16, 16, 16, 14]
TOTAL_GIFT_HEIGHT = [0, 8, 22, 36, 50, 64, 72]

class PhysicsEntity:
	def __init__(self, game, e_type, pos):
		self.game = game
		self.e_type = e_type
		self.pos = pos

		self.direction = [0, 0]

		self.action = ''
		self.anim_offset = [0, 0, 0, 0]
		self.flip = False


	def rect(self):
		return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])


	def update(self):
		pass

class Dino(PhysicsEntity):
	def __init__(self, game, pos, type, index):
		super().__init__(game, "dino", pos)
		
		self.index = index
		self.conversation = load_json('assets/conversation/' + str(index) + '.json')

		self.size = (16, 16)

		self.action = 'idle'
		self.flip = True

		self.animation = self.game.assets['dino/' + str(type)].copy()
		self.anim_offsets = self.game.assets['dino/1/offset']
		
		self.milk = 0
		self.milk_offsets = [[4, 5], [4, 4], [4, 5], [4, 5]]

		self.in_conver = False


	def update_animation(self):
		self.animation.update()
		self.img = pygame.Surface((self.animation.img().get_width(), self.animation.img().get_height()))
		self.img.set_colorkey((255, 0, 0))
		self.img.fill((255, 0, 0))
		self.img.blit(self.animation.img(), (0 , (self.img.get_height() - self.animation.img().get_height())))

	def anim_index(self):
		return int(self.animation.frame / self.animation.img_dur)


	def update(self):
		super().update()

		self.update_animation()

		self.direction[1] += 0.2

		self.pos[1] += self.direction[1]
		entity_rect = self.rect()

		for hitbox in self.game.map.hitboxs_around(self.pos, self.size):
			hitbox_r = pygame.Rect(hitbox['pos'][0]*16, hitbox['pos'][1]*16, 16, 16)
			if(entity_rect.colliderect(hitbox_r)):
				if(self.direction[1] > 0):
					entity_rect.bottom = hitbox_r.top
					self.direction[1] = 0
				else:
					entity_rect.top = hitbox_r.bottom
					self.direction[1] = 0

		self.pos[1] = entity_rect.y

		self.pos[0] += self.direction[0]
		entity_rect = self.rect()

		for hitbox in self.game.map.hitboxs_around(self.pos, self.size):
			hitbox_r = pygame.Rect(hitbox['pos'][0]*16, hitbox['pos'][1]*16, 16, 16)
			if(entity_rect.colliderect(hitbox_r)):
				if(self.direction[0] > 0):
					entity_rect.right = hitbox_r.left
					self.direction[0] = 0
				else:
					entity_rect.left = hitbox_r.right
					self.direction[0] = 0

		self.pos[0] = entity_rect.x

		entity_rect = self.rect()
		for milk in self.game.milks.milks:
			if(milk.status == 0):
				continue
			milk_r = milk.rect()
			if(pygame.rect.Rect.colliderect(entity_rect ,milk_r)):
				if(not self.milk):
					self.milk += 1
					milk.status = -1

					self.in_conver = True
					self.game.in_conver = True
					self.game.conversation = self.conversation
					self.game

		if(self.in_conver):
			self.game.conver_avt = self.img


	def render(self, surf, offset=(0, 0)):
		self.anim_offset = self.anim_offsets[str(int(self.animation.frame / self.animation.img_dur) + 1)]
		# pygame.draw.rect(surf, (255, 0, 0), (self.rect().left - offset[0], self.rect().top - offset[1], self.rect().width, self.rect().height))
		surf.blit(pygame.transform.flip(self.img, self.flip, False), (self.pos[0] - offset[0] -self.anim_offset[0], self.pos[1] -self.anim_offset[1] - offset[1]))

		
		if(self.milk):
			milk_img = self.game.assets['milk'][0]
			milk_offset = self.milk_offsets[self.anim_index()]
			dino_rect = self.rect()
			pos = (dino_rect.left + milk_offset[0] , dino_rect.top - 1 * milk_img.get_height() + milk_offset[1] + 2)
			
			render_pos = (pos[0] - offset[0] - 5, pos[1] - offset[1] - 8)
			surf.blit(milk_img, render_pos)



class Player(PhysicsEntity):
	def __init__(self, game, pos):
		super().__init__(game, 'player', pos)

		self.size = (16, 16)

		self.speed = 2
		self.can_move = True
		self.collisions = {'left': False, 'right': False, 'top': False, 'bottom': 'False'}

		self.gravity = 0.2
		
		self.can_jump = True
		self.jump_speed = 4


	def rect(self):
		return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

	def center(self):
		return self.rect().center

	def get_offset(self):
		return self.anim_offset

	def anim_index(self):
		return int(self.animation.frame / self.animation.img_dur)

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
		for hitbox in self.game.map.hitboxs_around(self.pos, self.size) + self.game.milks.milks_around(self.pos, self.size):
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

		for hitbox in self.game.map.hitboxs_around(self.pos, self.size) + self.game.milks.milks_around(self.pos, self.size):
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

	def set_action(self, action):
		if action != self.action:
			self.action = action
			self.animation = self.game.assets['player/' + self.action].copy()
			self.anim_offsets = self.game.assets['player/' + self.action + '/offset']
	
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

		self.anim_offset = self.anim_offsets[str(self.anim_index() + 1)]

		self.animation.update()
		self.img = pygame.Surface((self.animation.img().get_width(), self.animation.img().get_height()))
		self.img.set_colorkey((255, 0, 0))
		self.img.fill((255, 0, 0))
		self.img.blit(self.animation.img(), (0 , (self.img.get_height() - self.animation.img().get_height())))

		self.direction[0] = 0
		self.collisions = {'left': False, 'right': False, 'top': False, 'bottom': False}

	def update(self):
		super().update()
		self.update_moverment()
		self.update_animation()

	def render(self, surf, offset=(0, 0)):
		
		# pygame.draw.rect(surf, (255, 0, 0), (self.rect().left - offset[0], self.rect().top - offset[1], self.rect().width, self.rect().height))
		surf.blit(pygame.transform.flip(self.img, self.flip, False), (self.pos[0] - offset[0]- self.anim_offset[0], self.pos[1] - self.anim_offset[1] - offset[1]))

