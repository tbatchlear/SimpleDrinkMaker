import unittest
import tests
import os
import shutil

test_suite = unittest.TestLoader().discover('tests', pattern='test*')
unittest.TextTestRunner(verbosity=2).run(test_suite)

try:
    print(">Deleting test database and cache")
    os.remove('tests/test.db')
    shutil.rmtree('tests/__pycache__', ignore_errors=True)
except:
    print(">Could not automatically delete test database and cache.")
    pass