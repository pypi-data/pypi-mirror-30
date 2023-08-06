import unittest
from wml_runner import *


if __name__ == '__main__':
    suite = unittest.TestLoader().discover(start_dir="../svt", pattern="test_tensorflow_experimen*.py")

    runner = WMLRunner(test_cases=suite, environment=None, passrate_filename="svt_all", test_output_dir="svt_all", spark_required=False, java_required=False)
    runner.run()
