import unittest
from wml_runner import *


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_scikit*.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_spark*.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_spss*.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_pmml*.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_load*.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_xgboost*.py"))

    runner = WMLRunner(test_cases=suite, environment=None, passrate_filename="svt_all", test_output_dir="svt_all", spark_required=False, java_required=False)
    runner.run()
