from __future__ import division

import numbers
import re
from clirender.screen import Screen
from exceptions import NoStretchError
from safe_eval import safeEval

class Layout(object):
	def __init__(self, root=None):
		self.screen = Screen()
		self.root = root

	def bind(self, root):
		self.root = root
	def unbind(self):
		self.root = None

	def render(self, force=False, clear=True):
		if self.root is None:
			raise ValueError("Cannot render layout without root node")

		if clear:
			self.screen.clear()

		self.root.render_offset = (0, 0)
		self.root.render_boundary_left_top = [0, 0]
		self.root.render_boundary_right_bottom = list(self.screen.terminal_size)
		self.root.render_parent_width = self.screen.terminal_size[0]
		self.root.render_parent_height = self.screen.terminal_size[1]
		self.root.parent = None
		self.root.gen_parent = None
		self.root.render_stretch = self.screen.terminal_size[0]
		self.root._completely_revoked = self.root._changed or force
		self.root._changed = False

		self.root.layout = self
		self.root.render()

	def calcRelativeSize(self, size, total, stretch=None, expression=True):
		if not expression:
			# Maybe just absolute integer or float?
			try:
				return float(size)
			except ValueError:
				pass

			# Percent?
			try:
				if size.endswith("%"):
					return float(size[:-1]) / 100 * total
			except ValueError:
				pass

			raise ValueError("Cannot parse %s as non-expression offset/size" % size)

		if not isinstance(size, str) and not isinstance(size, unicode):
			return self.calcRelativeSize(size, total, stretch=stretch, expression=False)


		if stretch is not None:
			stretch = self.calcRelativeSize(stretch, total)


		# Replace percents
		size = re.sub(r"\b([\d\.]+%)(?=\s|$)", lambda x: str(self.calcRelativeSize(x.group(1), total, stretch=stretch, expression=False)), size)

		try:
			data = {}
			if stretch is not None:
				data["stretch"] = stretch

			return safeEval(size, data)
		except NameError, e:
			if e.message.split("'")[1] == "stretch":
				raise NoStretchError()

			raise e