import sys
import pygame as p
from search import Problem, ASearch, DFS, BFS

class Color:
	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)
	GRAY = (226, 226, 226)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	SKYBLUE = (0, 255, 255)
	YELLOW = (255, 255, 0)

class Visualizer:
	def __init__(self, width, height):
		# Window params
		self.WINDOW_HEIGHT = 600
		self.BLOCK_SIZE = self.WINDOW_HEIGHT // height
		self.GRID_WIDTH = self.BLOCK_SIZE // 60 + 1
		self.WINDOW_WIDTH = self.BLOCK_SIZE * width
		self.window = p.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

		# Game loop
		self.running = True
		self.drag = False
		self.clock = p.time.Clock()
		self.FPS = 60
		self.speed = width * height // 7

		# Modes: ['s', 'g', 'o', 'c']
		self.mode = 's'
		self.MODE_COLOR = {'s': Color.GREEN, 'g': Color.RED, 'o': Color.GRAY, 'c': Color.BLACK}
		self.width, self.height = width, height
		self.s = None
		self.g = None
		self.o = []
		self.problem = None
		self.algo = ASearch
		self.search = None
		self.solver = None
		self.solution = None
		self.steps = None

	def handleMouseEvent(self, e):
		if e.type == p.MOUSEBUTTONDOWN:
			self.drag = True
		else:
			self.drag = False
			self.update_problem()

	def handleKeyEvent(self, key):
		key_to_mode = {p.K_s: 's', p.K_g: 'g', p.K_o: 'o', p.K_c: 'c'}
		key_to_algo = {p.K_a: ASearch, p.K_d: DFS, p.K_b: BFS}
		key_to_size = {p.K_UP: (0, 1), p.K_DOWN: (0, -1), p.K_RIGHT: (1, 0), p.K_LEFT: (-1, 0)}

		if key in key_to_mode.keys():
			self.mode = key_to_mode[key]
		elif key in key_to_algo.keys():
			self.algo = key_to_algo[key]
		elif key in key_to_size.keys():
			self.width, self.height = self.width + key_to_size[key][0], self.height + key_to_size[key][1]
			self.update_problem()
		elif key == p.K_SPACE and self.problem is not None:
			self.FPS = self.speed
			self.search = self.algo(self.problem)
			self.solver = self.search.run()

	def update_problem(self):
		self.BLOCK_SIZE = self.WINDOW_HEIGHT // self.height
		self.GRID_WIDTH = self.BLOCK_SIZE // 60 + 1
		self.WINDOW_WIDTH = self.BLOCK_SIZE * self.width
		self.window = p.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
		self.speed = min(60, self.width * self.height // 7)

		if self.s is not None and self.g is not None:
			self.problem = Problem(self.width, self.height, self.s, self.g, self.o)
		else:
			self.problem = None	

	def get_solution_steps(self):
		for i in range(len(self.solution)):
			yield self.solution[:i+1]

	def reset(self):
		self.running = True
		self.drag = False
		self.s = None
		self.g = None
		self.o = []
		self.problem = None
		self.algo = ASearch
		self.search = None
		self.solver = None
		self.solution = None
		self.steps = None		
		self.update_problem()

	def draw(self):
		self.window.fill(Color.BLACK)
		x, y = p.mouse.get_pos()
		m_c, m_r = x // self.BLOCK_SIZE, y // self.BLOCK_SIZE

		# Get open / closed list
		if self.solver is not None:
			try:
				ol, cl = next(self.solver)
			except StopIteration:
				ol, cl = [], []
				self.solution = self.search.solution
				self.FPS *= 3
				if self.steps is None and self.solution is not None:
					self.steps = self.get_solution_steps()

		if self.steps is not None:
			try:
				steps = next(self.steps)
			except StopIteration:
				steps = self.solution
				self.FPS = 60

		for c in range(self.width):
			for r in range(self.height):
				in_rect = p.Rect(c * self.BLOCK_SIZE + self.GRID_WIDTH, r * self.BLOCK_SIZE + self.GRID_WIDTH, self.BLOCK_SIZE - 2 * self.GRID_WIDTH, self.BLOCK_SIZE - 2 * self.GRID_WIDTH)
				color = Color.BLACK
				# Draw mouse position
				if c <= m_c < (c + 1) and r <= m_r < (r + 1) and self.solver is None:
					color = self.MODE_COLOR[self.mode]

				# Draw open list if solved
				if self.solver is not None and (c, r) in ol:
					color = Color.SKYBLUE

				# Draw closed list if solved
				elif self.solver is not None and (c, r) in cl:
					color = Color.BLUE

				# Draw start square
				if (c, r) == self.s:
					color = self.MODE_COLOR['s']

				# Draw goal square
				elif (c, r) == self.g:
					color = self.MODE_COLOR['g']

				# Draw obstacle square
				elif (c, r) in self.o:
					color = self.MODE_COLOR['o']

				# Draw mouse position on cancel mode
				if c <= m_c < (c + 1) and r <= m_r < (r + 1) and self.mode == 'c' and self.solver is None:
					color = self.MODE_COLOR['c']

				# Draw solution if solved
				if self.steps is not None and (c, r) in steps:
					color = Color.YELLOW

				p.draw.rect(self.window, color, in_rect)

				# Draw Grid
				rect = p.Rect(c * self.BLOCK_SIZE, r * self.BLOCK_SIZE, self.BLOCK_SIZE, self.BLOCK_SIZE)
				p.draw.rect(self.window, Color.WHITE, rect, self.GRID_WIDTH)

		p.display.update()

	def run(self):
		while self.running:
			self.clock.tick(self.FPS)
			for e in p.event.get():
				if e.type == p.QUIT:
					self.running = False
					p.quit()
					sys.exit()
				elif e.type == p.KEYDOWN and e.key == p.K_r:
					self.reset()
				elif e.type == p.KEYDOWN and self.solution is None:
					self.handleKeyEvent(e.key)
				elif (e.type == p.MOUSEBUTTONDOWN or e.type == p.MOUSEBUTTONUP) and self.solution is None:
					self.handleMouseEvent(e)

			if self.drag:
				x, y = p.mouse.get_pos()
				c, r = x // self.BLOCK_SIZE, y // self.BLOCK_SIZE
				if self.mode == 's' and (c, r) not in self.o and (c, r) != self.g:
					self.s = (c, r)
				elif self.mode == 'g' and (c, r) not in self.o and (c, r) != self.s:
					self.g = (c, r)
				elif self.mode == 'o' and (c, r) != self.s and (c, r) != self.g:
					self.o.append((c, r)) 
				elif self.mode == 'c':
					if (c, r) == self.s:
						self.s = None
					elif (c, r) == self.g:
						self.g = None
					elif (c, r) in self.o:
						self.o.remove((c, r))

			self.draw()


if __name__ == '__main__':
	Visualizer(7, 5).run()
