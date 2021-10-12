from io import StringIO
import unittest
from cuboid_test import *
from pprint import pprint
stream = StringIO()
runner = unittest.TextTestRunner(stream=stream)
result = runner.run(unittest.makeSuite(TestCuboid))
# unittest.main(argv=[''], verbosity = 0, exit=False)
pprint (result.testsRun)
pprint (result.errors)
pprint (result.failures)
# stream.seek(0)
# print 'Test output\n', stream.read()