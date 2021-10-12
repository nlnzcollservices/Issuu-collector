import unittest
from cuboid import *

class TestCuboid(unittest.TestCase):
	def test_parse_(self):
		self.assertAlmostEqual(cuboid(2),8)
		self.assertAlmostEqual(cuboid(1),1)
		self.assertAlmostEqual(cuboid(0),0)
		self.assertAlmostEqual(cuboid(5.5),0)
	def test_input_value(self):
		self.assertRaises(TypeError, cuboid, True)
