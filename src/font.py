import pygame
from src.utils import load_font, clip, replace_color


class Font:
	def __init__(self):

		font_img = load_font('large_font.png')
		self.line_height = font_img.get_height()
		self.font_order = ['A','B',' ','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';']
		self.font = {}

		last_x = 0
		letter_index = 0
		for x in range(font_img.get_width()):
			if font_img.get_at((x, 0))[0] == 127:
				self.font[self.font_order[letter_index]] = clip(font_img, pygame.Rect(last_x, 0, x - last_x, font_img.get_height()))
				letter_index += 1
				last_x = x + 1


	def render(self, surf, text, color=(0, 0, 0), base_space = 6, line_space=8, letter_spacing=4):
		width, height = surf.get_size()
		font = self.font.copy()
		for key in font:
			font[key] = replace_color(font[key], (255, 0, 0), color)

		words = text.split(' ')
		x = 0
		y = 0
		for word in words:
			word_width = -letter_spacing
			for char in word:
				word_width += font[char].get_width() + letter_spacing
			if(x + word_width >= width):
				x = 0
				y = y + self.line_height + line_space
			for char in word:
				surf.blit(font[char], (x, y))
				x = x + font[char].get_width() + letter_spacing
			
			x += base_space + letter_spacing