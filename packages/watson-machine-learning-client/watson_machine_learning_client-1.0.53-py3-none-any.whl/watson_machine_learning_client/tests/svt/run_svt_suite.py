import os
import unittest
import timeit
import sys
from os.path import join as path_join

os.environ['ENV'] = "YP"
stream = sys.stderr

if "SPARK_HOME" not in os.environ:
    stream.write("Test suite interrupted, reason: SPARK_HOME is not set")
    quit()
if "JAVA_HOME" not in os.environ:
    stream.write("Test suite interrupted, reason: JAVA_HOME is not set")
    quit()

SPARK_HOME_PATH = os.environ['SPARK_HOME']
PYSPARK_PATH = str(SPARK_HOME_PATH) + "/python/"
sys.path.insert(1, path_join(PYSPARK_PATH))


import test_scikit_learn_from_object
import test_scikit_xgboost_from_object
import test_spark_mllib_from_object
import test_spss_from_file
import test_tensorflow_from_directory
import test_tensorflow_from_file
import test_tensorflow_from_training_s3
import test_xgboost_from_object
import xmlrunner

execution_output_file = open("execution_run_all_local.log", "w")
passrate_file = open("passratepythonclient.prop", "w")

test_suites = [test_scikit_learn_from_object,
               test_scikit_xgboost_from_object,
               test_spark_mllib_from_object,
               test_spss_from_file,
               test_tensorflow_from_directory,
               test_tensorflow_from_file,
               test_tensorflow_from_training_s3,
               test_xgboost_from_object]


def run_tests():
    tests = 0
    failures = 0
    skipped = 0
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    for test in test_suites:
        stream.write("Suite: {} started.".format(str(test.__name__)))
        execution_output_file.write("Suite: {} started.\n".format(str(test.__name__)))

        started_at = timeit.default_timer()
        result = runner.run(create_suite(test))
        elapsed = timeit.default_timer() - started_at
        stream.write("Suite finished in {:06.2f}s. Test: {}, Failures: {}, Skipped: {}".format(
            elapsed, result.testsRun, len(result.errors), len(result.skipped)))
        execution_output_file.write("Suite finished in {:06.2f}s. Test: {}, Failures: {}, Skipped: {}\n".format(
            elapsed, result.testsRun, len(result.errors), len(result.skipped)))

        tests += result.testsRun
        failures += len(result.errors)
        skipped += len(result.skipped)

    return (tests, failures, skipped)


def create_suite(test_module):
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromModule(module=test_module))
    return test_suite


if __name__ == '__main__':
    stream.write("Run suites: ")
    execution_output_file.write("Run suites:\n")

    started_at = timeit.default_timer()
    result = run_tests()
    elapsed = timeit.default_timer() - started_at

    stream.write("Run finished. Execution time: {:06.2f}s. Tests: {}, Failures: {}, Skipped: {}".format(
        elapsed, result[0], result[1], result[2]))
    execution_output_file.write("Run finished.\nExecution time: {:06.2f}s.\nTotalTestcases: {}\nTotalFailures: {}\nTotalSkipped: {}".format(
        elapsed, result[0], result[1], result[2]))
    execution_output_file.close()

    passrate_file.write("PASSRATE20={:05.2f}\n".format((result[0] - result[1])/result[0]*100))
    passrate_file.write("Ignored_Tc={}\n".format(str(result[2])))
    passrate_file.write("Succeeded={}\n".format(str(result[0]-result[1])))
    passrate_file.write("Failed={}\n".format(str(result[1])))
    passrate_file.write("Total_Testcase={}\n".format(str(result[0])))
    passrate_file.write("Duration={}\n".format(str(int(elapsed/60))))

    passrate_file.close()
