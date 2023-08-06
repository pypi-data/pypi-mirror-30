from nodes import Node, Generator

class NodeAPI(object):
	def getBoundaryBox(self):
		node = storage[self]
		if isinstance(node, Node):
			return node.getBoundaryBox()
		else:
			raise self._unexpectedType("getBoundaryBox()")


	@property
	def childNodes(self):
		node = storage[self]
		if isinstance(node, Node):
			return map(createAPI, node._children)
		elif isinstance(node, Generator):
			return map(createAPI, node.generate())
		else:
			raise self._unexpectedType("childNodes")

	@property
	def children(self):
		node = storage[self]
		if isinstance(node, Node):
			return map(createAPI, node.children)
		elif isinstance(node, Generator):
			return map(createAPI, self._get_children_recursively(node))
		else:
			raise self._unexpectedType("children")

	def _get_children_recursively(self, generator):
		res = []
		for node in generator.generate():
			if isinstance(node, Generator):
				res += self._get_children_recursively(node)
			else:
				res.append(node)
		return res


	@property
	def parent(self):
		node = storage[self]
		return createAPI(node.gen_parent)


	def isNode(self):
		node = storage[self]
		return isinstance(node, Node)
	def isGenerator(self):
		node = storage[self]
		return isinstance(node, Generator)


	@property
	def nodeName(self):
		node = storage[self]
		return node.__class__.__name__


	def __getitem__(self, name):
		node = storage[self]
		if name not in node.properties:
			raise ValueError("[]: %s is not a property" % name)
		return getattr(node, name)

	def __setitem__(self, name, value):
		node = storage[self]
		if name not in node.properties:
			raise ValueError("[]: %s is not a property" % name)
		setattr(node, name, value)

		node._completely_revoked = True
		while node is not None:
			node._revoked = True
			node = node.parent


	def _unexpectedType(self, callee):
		node = storage[self]
		return ValueError("%s: Not defined on %s" % (callee, type(node)))


# storage[self] is a way to simulate private scope, so that Node or Generator
# couldn't be accessed from outside
storage = dict()

def createAPI(node):
	class LocalNodeAPI(NodeAPI):
		def __init__(self):
			storage[self] = node
			super(LocalNodeAPI, self).__init__()

	return LocalNodeAPI()