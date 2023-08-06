import unittest
from wml_runner import *


if __name__ == '__main__':
    test_cases = unittest.TestLoader().discover(start_dir="../svt", pattern="test_scikit_learn_from_object.py")

    runner = WMLRunner(test_cases=test_cases, environment=None, passrate_filename="svt_all", test_output_dir="svt_all", spark_required=False, java_required=False)
    runner.run()
