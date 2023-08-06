import unittest
from wml_runner import *


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_tensorflow_distributed_ddl_experiment.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_tensorflow_training.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_tensorflow_training_mandatory_params_only.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_keras_experiment.py"))
    suite.addTest(unittest.TestLoader().discover(start_dir="../svt", pattern="test_pytorch_experiment.py"))

    runner = WMLRunner(test_cases=suite, environment=None, passrate_filename="svt_all", test_output_dir="svt_all", spark_required=False, java_required=False)
    runner.run()
