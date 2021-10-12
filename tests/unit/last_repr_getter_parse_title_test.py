import unittest
import platform
import sys
from io import StringIO
from pprint import pprint
os_name = platform.system()
if os_name == "Windows":
	slash = "\\"
else:
	slash = "/"
import os
# print(os.path.abspath(os.getcwd()))
# print(os.path.abspath(__file__))#.split(slash)[:-2].append("scripts")))
# print(type(os.path.abspath(__file__).split(slash)[:-3]))
new_path_list = os.path.abspath(__file__).split(slash)[:-3] + ["scripts"]
# print(slash.join(new_path_list))
sys.path.insert(0,slash.join(new_path_list))
print(sys.path)
from last_representation_getter import parse_the_labels

# assertEqual(a, b)
# assertNotEqual(a, b)
# assertTrue(x)
# assertFalse(x)
# assertIs(a, b)
# assertIsNot(a, b)
# assertIsNone(x)
# assertIsNotNone(x)
# assertIn(a, b)
# assertNotIn(a, b)
# assertIsInstance(a, b)
# assertNotIsInstance(a, b)
# assertRaises(exc, fun, args, *kwds)
# assertRaisesRegexp(exc, r, fun, args, *kwds)
# assertAlmostEqual(a, b)
# assertNotAlmostEqual(a, b)
# assertGreater(a, b)
# assertGreaterEqual(a, b)
# assertLess(a, b)
# assertLessEqual(a, b)
# assertRegexpMatches(s, r)
# assertNotRegexpMatches(a, b)
# assertDictContainsSubset(a, b)

class TestLastRepresentationGetter(unittest.TestCase):
	def test_volume(self):
		self.assertAlmostEqual(parse_the_labels("2014 09 11"),('2014 09 11', None, None, None, None, None, '09', '2014', False, True))
		self.assertAlmostEqual(parse_the_labels("2013 Summer"),('2013 January 01', None, None, None, 'Summer', 'January', None, '2013', True, True))
		self.assertAlmostEqual(parse_the_labels("no.700 2014 05 16"),('2014 05 16', None, None, '700', None, None, '05', '2014', False, True))
		self.assertAlmostEqual(parse_the_labels("iss.803 2016 05 13"),('2016 05 13', None, '803', None, None, None, '05', '2016', False, True))
		self.assertAlmostEqual(parse_the_labels("2018 09"),('2018 09 01', None, None, None, None, None, '09', '2018', False, True))
		self.assertEqual(parse_the_labels("2021 July 01"),('2021 01 01', None, None, None, None, 'July', '01', '2021', False, True))

	# def test_input_value(self):
	# 	self.assertRaises(TypeError, parse_the_labels, True)







def main():


	stream = StringIO()
	runner = unittest.TextTestRunner(stream=stream)
	result = runner.run(unittest.makeSuite(TestLastRepresentationGetter))
	# unittest.main(argv=[''], verbosity = 0, exit=False)
	print(dir(result))
	pprint (result.testsRun)
	print("here0")
	pprint (result.errors)
	print("here1")
	pprint (result.failures)
	print("here2")

if __name__ == '__main__':
	main()