import math

class Node:
	def __init__(self, state, parent = None):
		self.state = state
		self.parent = parent
		self.children = []
		self.depth = self.parent.depth + 1 if self.parent is not None else 0


class Problem:
	def __init__(self, width, height, start_state, goal_state, obstacles):
		self.width = width
		self.height = height
		self.start_state = start_state
		self.goal_state = goal_state
		self.obstacles = obstacles

	def goal(self, node):
		return node.state == self.goal_state

	def is_valid_state(self, s):
		if 0 <= s[0] < self.width and 0 <= s[1] < self.height and s not in self.obstacles:
			return True
		return False

	def show(self, ol, cl):
		for r in reversed(range(self.height)):
			s = ''
			for c in range(self.width):
				if (c, r) == self.goal_state:
					s += 'G '
				elif (c, r) in self.obstacles:
					s += '- '
				elif (c, r) in cl:
					s += 'x '
				elif (c, r) in ol:
					s += '/ '
				else:
					s += '. '
			print(s)

	@property
	def operators(self):
		return [lambda s: (s[0], s[1] - 1), 
				lambda s: (s[0] + 1, s[1] - 1),
				lambda s: (s[0] + 1, s[1]), 
				lambda s: (s[0] + 1, s[1] + 1), 
				lambda s: (s[0], s[1] + 1), 
				lambda s: (s[0] - 1, s[1] + 1), 
				lambda s: (s[0] - 1, s[1]), 
				lambda s: (s[0] - 1, s[1] - 1) 				
				]


class Search:
	def __init__(self, problem):
		self.open_list = [Node(problem.start_state)]
		self.open_list_state = [problem.start_state]
		self.closed_list = []
		self.problem = problem
		self.solution = None

	# Expand
	def expand_node(self, node):
		return NotImplementedError()

	# Traverse
	def traverse(self, node):
		# print(f'Traversing {node.state} / Depth: {node.depth} / Eval: {self.f(node)}')
		self.closed_list.append(node.state)
		self.expand_node(node)
		# self.problem.show(self.open_list_state, self.closed_list)

	# Run search
	def run(self):
		while len(self.open_list) > 0:
			node = self.open_list.pop(0)
			# If node is goal
			if self.problem.goal(node):
				solution = [node.state]
				while node.parent is not None:
					solution.append(node.parent.state)
					node = node.parent
				self.solution = list(reversed(solution))
				print(f'Found solution: {self.solution}')
				return True
			# If not goal, keep searching
			self.traverse(node)
			yield self.open_list_state, self.closed_list

		# print(f'Failed to find solution.')
		return False


class DFS(Search):
	def expand_node(self, node):
		new_nodes = []
		for op in self.problem.operators:
			new_state = op(node.state)
			if self.problem.is_valid_state(new_state) and new_state not in self.closed_list and new_state not in self.open_list_state:
				child = Node(new_state, node)
				node.children.append(child)
				new_nodes.append(child)

		self.open_list = new_nodes + self.open_list
		self.open_list_state = [n.state for n in self.open_list]


class BFS(Search):
	def expand_node(self, node):
		for op in self.problem.operators:
			new_state = op(node.state)
			if self.problem.is_valid_state(new_state) and new_state not in self.closed_list and new_state not in self.open_list_state:
				child = Node(new_state, node)
				node.children.append(child)
				self.open_list.append(child)

		self.open_list_state = [n.state for n in self.open_list]


class ASearch(Search):
	# Admissible heuristic 
	def h(self, node):
		d0 = self.problem.goal_state[0] - node.state[0]
		d1 = self.problem.goal_state[1] - node.state[1]
		return math.sqrt(d0 ** 2 + d1 ** 2)

	# Eval function
	def f(self, node):
		return node.depth + self.h(node)

	# Expand
	def expand_node(self, node):
		for op in self.problem.operators:
			new_state = op(node.state)
			if self.problem.is_valid_state(new_state) and new_state not in self.closed_list and new_state not in self.open_list_state:
				child = Node(new_state, node)
				node.children.append(child)
				self.open_list.append(child)

		self.open_list = sorted(self.open_list, key=lambda n: self.f(n))
		self.open_list_state = [n.state for n in self.open_list]


if __name__ == '__main__':
	# Define problem
	w, h = 7, 5
	s, g = (1, 2), (6, 2)
	o = [(4, 4), (4, 3), (4, 2), (4, 1)]
	p = Problem(w, h, s, g, o)

	# solver = ASearch(p).run()
	# solver = DFS(p).run()
	
	# Solve
	while True:
		try:
			ol, cl = next(solver)
		except StopIteration:
			break
