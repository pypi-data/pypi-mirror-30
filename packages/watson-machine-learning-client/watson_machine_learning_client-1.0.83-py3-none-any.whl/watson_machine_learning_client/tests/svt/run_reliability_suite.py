import os
import unittest
import timeit
import xmlrunner

os.environ['ENV'] = "SVT"

if "SPARK_HOME" not in os.environ:
    print("Test suite interrupted, reason: SPARK_HOME is not set")
    quit()
if "JAVA_HOME" not in os.environ:
    print("Test suite interrupted, reason: JAVA_HOME is not set")
    quit()

# TEST CONFIGURATION
# run_module - test module used in test
# iterations - number of test iteration

import test_tensorflow_from_directory as run_module
iterations = 2

passrate_file = open("passratereliability.prop", "w")


class TestExecutor:

    def __init__(self, repeats):
        self._repeats = repeats
        self._runner = xmlrunner.XMLTestRunner(output="reliability_reports")
        self._runs = []
        self._tests_executed = 0
        self._tests_failures = 0
        self._tests_skipped = 0

    def execute(self):
        print("Execution started.")
        self._test_started_at = timeit.default_timer()

        for i in range(0, self._repeats):
            print("  Suite {} run.\n".format(i))

            suite_started_at = timeit.default_timer()
            result = self.run_suite()
            elapsed = timeit.default_timer() - suite_started_at

            print("  Suite {} finished in {:06.2f}s.\n".format(i, elapsed))

            self._runs.append((i, result.testsRun, len(result.errors), len(result.skipped), elapsed))
            self._tests_executed += result.testsRun
            self._tests_failures += len(result.errors)
            self._tests_skipped += len(result.skipped)

        self._test_elapsed = timeit.default_timer() - self._test_started_at

        print("Execution finished in {:06.2f}s.\n".format(self._test_elapsed))

    def run_suite(self):
        return self._runner.run(self.suite())

    def suite(self):
        loader = unittest.TestLoader()
        test_suite = unittest.TestSuite()
        test_suite.addTest(loader.loadTestsFromModule(run_module))
        return test_suite

    def print_result(self):
        print("Summary:")
        print("Suites: {}, Tests: {}, Failed tests: {}, Skipped tests: {}, Time: {:06.2f}s".format(
            len(self._runs), self._tests_executed, self._tests_failures, self._tests_skipped, self._test_elapsed))
        for run in self._runs:
            print("Run: {}, Executed: {}, Failures: {}, Skipped: {}, Time: {:06.2f}s".format(
                run[0], run[1], run[2], run[3], run[4]))

    def get_results(self):
        return(self._tests_executed, self._tests_failures, self._tests_skipped, self._test_elapsed)


if __name__ == '__main__':
    executor = TestExecutor(repeats=iterations)
    executor.execute()
    executor.print_result()

    result = executor.get_results()
    passrate_file.write("PASSRATE20={:05.2f}\n".format((result[0] - result[1]) / result[0] * 100))
    passrate_file.write("Ignored_Tc={}\n".format(str(result[2])))
    passrate_file.write("Succeeded={}\n".format(str(result[0] - result[1])))
    passrate_file.write("Failed={}\n".format(str(result[1])))
    passrate_file.write("Total_Testcase={}\n".format(str(result[0])))
    passrate_file.write("Duration={}\n".format(str(int(result[3] / 60))))

    passrate_file.close()
