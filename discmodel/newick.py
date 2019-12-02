def convert_tree(pi, tau):

	def child_is_empty(node):
		'''
		Checks if a node contains any children
		'''	
		return tree[node] == []

	def get_parent(node):
		'''
		Returns the parent node of a given node.
		'''
		for n in tree.keys():
			if node in tree[n]:
				return n

	def total_coalescence():
		'''
		Returns the total time it takes for all lineages to
		coalesce.
		'''	
		return tau[-1]

	def to_string(node):
		if node < 10:
            		return "s000"+str(node)
		if node < 100:
			return "s00"+str(node)
		if node < 1000:
			return "s0"+str(node)
		return "s" +str(node)
	def get_coalescence(node):
		'''
		Takes a node and returns the length of the branch from
		the node to the parent. Only need to check when a node
		has children.
		'''
		parent = get_parent(node)
		if child_is_empty(node):
			return tau[parent]
		else:
			return tau[parent] - tau[node]

	def convert(node):
		'''
		Runs the actual conversion. This function searches recursively
		through the tree from the top node down.
		'''
		string = '('
		children = tree[node]
		
		for child in children:
			coal = str(round(get_coalescence(child), 2))
			if child_is_empty(child):
				string += to_string(child) + ':' + coal
			else:
				string += convert(child)
			if child != children[-1]:
				string += ','

		if node != len(tau) - 1:
			coal = str(round(get_coalescence(node), 2))
			string +='):' + coal
		else:
			string += ');'
		return string

	tree = construct_tree(pi)
	return convert(len(tau) - 1)



def fix_pi_tau(pi, tau):
	'''
	Converts multifurcating trees to bifurcating trees
	by adding 0.0 branch lengths.
	'''
	coalescence_map = {}
	for index in range(len(pi)):
		coalescence_map[index] = {pi[index]: tau[index]}

	parent_children = construct_tree(pi)

	for parent, children in parent_children.items():
		if len(children) > 2:
			if parent == len(pi) - 1:
				coalescence_map[children[2]] = {parent + 1: tau[children[2]]}
				coalescence_map[parent] = {parent + 1: tau[parent]}
				coalescence_map[len(pi)] = {0: tau[-1]}

			else:
				coalescence_map[children[0]] = {len(pi) - 1: tau[children[0]]}
				coalescence_map[children[1]] = {len(pi) - 1: tau[children[1]]}
				coalescence_map[len(pi) - 1] = {parent: tau[parent]}
				coalescence_map[len(pi)] = {0: tau[-1]}

				change_children = parent_children[len(pi) - 1]
				for child in change_children:
						coalescence_map[child] = {len(pi): tau[child]}
				break

	new_pi = []
	new_tau = []
	for index in sorted(coalescence_map.keys()):
		new_pi.append(int(list(coalescence_map[index].keys())[0]))
		new_tau.append(list(coalescence_map[index].values())[0])

	bifurcating = True
	for children in construct_tree(new_pi).values():
		if len(children) > 2:
			bifurcating = False

	if bifurcating:
		return new_pi, new_tau
	else:
		return fix_pi_tau(new_pi, new_tau)



def construct_tree(pi):
	'''
	Constructs a dictionary. Each key is an integer that corresponds to
	a node in the tree, and each value is a list of integers that correspond
	to the children nodes. If a node has no children, an empty list is returned.
	'''
	tree = {}
	for n in range(1, len(pi)):
		tree[n] = []
	for n in range(1, len(pi)):
		if int(pi[n]) != 0:
			tree[int(pi[n])].append(n)
	return tree



def convert_to_newick(pi, tau, bifurcate):

	pi = str(pi).lstrip('[').rstrip(']').split(',')
	pi = list(map(lambda i: int(i), pi))
	tau = str(tau).lstrip('[').rstrip(']').split(',')
	tau = list(map(lambda j: float(j), tau))

	if bifurcate:
		fixed = fix_pi_tau(pi, tau)
		pi = fixed[0]
		tau = fixed [1]

	return convert_tree(pi, tau)
