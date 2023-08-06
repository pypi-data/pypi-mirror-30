import unittest
import os
from configparser import ConfigParser
import json
import boto3
import sys
import io
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.experiments import Experiments
from preparation_and_cleaning import *


class TestWMLClientWithExperiment(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    definition_1_uid = None
    definition_1_url = None
    definition_2_uid = None
    definition_2_url = None
    trained_model_uid = None
    experiment_uid = None
    experiment_run_uid = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithExperiment.logger.info("Service Instance: setting up credentials")
        self.wml_credentials = get_wml_credentials()
        # reload(site)
        self.client = get_client()
        self.cos_resource = get_cos_resource()
        prepare_cos(self.cos_resource)

    @classmethod
    def tearDownClass(self):
        clean_cos(self.cos_resource)

    def test_01_service_instance_details(self):
        TestWMLClientWithExperiment.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithExperiment.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithExperiment.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_save_definition1(self):
        TestWMLClientWithExperiment.logger.info("Save model definition ...")

        self.client.repository.DefinitionMetaNames.show()

        metadata = {
            self.client.repository.DefinitionMetaNames.NAME: "my_training_definition",
            self.client.repository.DefinitionMetaNames.DESCRIPTION: "my_description",
            self.client.repository.DefinitionMetaNames.AUTHOR_NAME: "John Smith",
            self.client.repository.DefinitionMetaNames.AUTHOR_EMAIL: "js@js.com",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.2",
            self.client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            self.client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            self.client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20"
            }

        model_content_path = './artifacts/tf-softmax-model.zip'
        definition_details = self.client.repository.store_definition(training_definition=model_content_path, meta_props=metadata)
        TestWMLClientWithExperiment.definition_1_uid = self.client.repository.get_definition_uid(definition_details)
        TestWMLClientWithExperiment.definition_1_url = self.client.repository.get_definition_url(definition_details)
        TestWMLClientWithExperiment.logger.info("Saved model definition uid: " + str(TestWMLClientWithExperiment.definition_1_uid))

    def test_03_save_definition2(self):
        TestWMLClientWithExperiment.logger.info("Save model definition ...")
        metadata = {
            self.client.repository.DefinitionMetaNames.NAME: "my_training_definition",
            self.client.repository.DefinitionMetaNames.DESCRIPTION: "my_description",
            self.client.repository.DefinitionMetaNames.AUTHOR_NAME: "John Smith",
            self.client.repository.DefinitionMetaNames.AUTHOR_EMAIL: "js@js.com",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.2",
            self.client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            self.client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            self.client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20"
            }

        model_content_path = './artifacts/tf-softmax-model.zip'
        definition_details = self.client.repository.store_definition(training_definition=model_content_path, meta_props=metadata)
        TestWMLClientWithExperiment.definition_2_uid = self.client.repository.get_definition_uid(definition_details)
        TestWMLClientWithExperiment.definition_2_url = self.client.repository.get_definition_url(definition_details)
        TestWMLClientWithExperiment.logger.info("Saved model definition uid: " + str(TestWMLClientWithExperiment.definition_2_uid))

    def test_04_get_definition_details(self):
        print("Getting definition details ...")
        details_1 = self.client.repository.get_definition_details(TestWMLClientWithExperiment.definition_1_uid)
        print(details_1)
        self.assertTrue('my_training_definition' in str(details_1))

        details_2 = self.client.repository.get_definition_details(TestWMLClientWithExperiment.definition_2_uid)
        print(details_2)
        self.assertTrue('my_training_definition' in str(details_2))

    def test_05_save_experiment(self):
        metadata = {
                    self.client.repository.ExperimentMetaNames.NAME: "my_experiment",
                    self.client.repository.ExperimentMetaNames.DESCRIPTION: "mnist best model",
                    self.client.repository.ExperimentMetaNames.AUTHOR_NAME: "John Smith",
                    self.client.repository.ExperimentMetaNames.AUTHOR_EMAIL: "js@js.com",
                    self.client.repository.ExperimentMetaNames.EVALUATION_METHOD: "multiclass",
                    self.client.repository.ExperimentMetaNames.EVALUATION_METRIC: "accuracy",
                    self.client.repository.ExperimentMetaNames.TRAINING_DATA_REFERENCE: {
                            "connection": {
                                "endpoint_url": "https://s3-api.us-geo.objectstorage.service.networklayer.com",
                                "aws_access_key_id": "zfho4HT7pUIStZvSkDsl",
                                "aws_secret_access_key": "21q66Vvxkhr4uPDacTf8F9fnzMjSUIzsZRtxrYbx"
                            },
                            "source": {
                                "bucket": "wml-dev",
                            },
                            "type": "s3"
                        },
                    self.client.repository.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE: {
                            "connection": {
                                "endpoint_url": "https://s3-api.us-geo.objectstorage.service.networklayer.com",
                                "aws_access_key_id": "zfho4HT7pUIStZvSkDsl",
                                "aws_secret_access_key": "21q66Vvxkhr4uPDacTf8F9fnzMjSUIzsZRtxrYbx"
                            },
                            "target": {
                                "bucket": "wml-dev-results",
                            },
                            "type": "s3"
                        },
                    self.client.repository.ExperimentMetaNames.TRAINING_REFERENCES: [
                        {
                            "name": "mnist_nn",
                            "training_definition_url": TestWMLClientWithExperiment.definition_1_url + '/content', # TODO without content
                            "command": "python3 mnist_softmax.py --trainingIters 20",
                            "compute_configuration": {"size": "medium", "gpu_type": "V100"}
                        },
                        {
                            "name": "mnist_cnn",
                            "training_definition_url": TestWMLClientWithExperiment.definition_2_url + '/content', # TODO without content
                            "command": "python3 mnist_lenet.py --trainingIters 20",
                            "compute_configuration": {"size": "medium", "gpu_type": "V100"}
                        },
                    ],
                }

        experiment_details = self.client.repository.store_experiment(meta_props=metadata)
        self.assertTrue('my_experiment' in str(experiment_details))

        TestWMLClientWithExperiment.experiment_uid = self.client.repository.get_experiment_uid(experiment_details)

        experiment_specific_details = self.client.repository.get_experiment_details(TestWMLClientWithExperiment.experiment_uid)
        self.assertTrue(TestWMLClientWithExperiment.experiment_uid in str(experiment_specific_details))

    def test_06_get_experiment_details(self):
        details = self.client.repository.get_experiment_details()
        self.assertTrue(TestWMLClientWithExperiment.experiment_uid in str(details))

        details2 = self.client.repository.get_experiment_details(TestWMLClientWithExperiment.experiment_uid)
        self.assertTrue(TestWMLClientWithExperiment.experiment_uid in str(details2))

    def test_07_run_experiment(self):
        created_experiment_run_details = self.client.experiments.run(TestWMLClientWithExperiment.experiment_uid, asynchronous=False)
        self.assertIsNotNone(created_experiment_run_details)
        TestWMLClientWithExperiment.experiment_run_uid = Experiments.get_run_uid(created_experiment_run_details)

    def test_08_get_status(self):
        status = self.client.experiments.get_status(TestWMLClientWithExperiment.experiment_run_uid)
        self.assertIsNotNone(status)

    #def test_09_monitor(self):
        # TODO add validation
        # self.client.experiments.monitor(TestWMLClientWithExperiment.experiment_run_uid)

    def test_10_get_all_experiments_runs_details(self):
        details = self.client.experiments.get_details()
        self.assertIsNotNone(details)

    def test_11_get_experiment_run_details(self):
        details = self.client.experiments.get_details(TestWMLClientWithExperiment.experiment_uid)
        self.assertIsNotNone(details)

    def test_12_get_experiment_run_details(self):
        details = self.client.experiments.get_run_details(TestWMLClientWithExperiment.experiment_run_uid)
        self.assertIsNotNone(details)

    def test_13_list_experiments(self):
        captured_output = io.StringIO()  # Create StringIO object
        sys.stdout = captured_output  # and redirect stdout.
        self.client.experiments.list()  # Call function.
        sys.stdout = sys.__stdout__  # Reset redirect.
        # TODO self.assertTrue(TestWMLClientWithExperiment.experiment_uid in captured_output.getvalue())
        self.client.experiments.list()  # Just to see values.

    def test_14_list_experiment_runs_for_experiment(self):
        captured_output = io.StringIO()  # Create StringIO object
        sys.stdout = captured_output  # and redirect stdout.
        self.client.experiments.list(TestWMLClientWithExperiment.experiment_uid)  # Call function.
        sys.stdout = sys.__stdout__  # Reset redirect.
        # TODO self.assertTrue(TestWMLClientWithExperiment.experiment_uid in captured_output.getvalue())
        self.client.experiments.list(TestWMLClientWithExperiment.experiment_uid)  # Just to see values.

    def test_15_delete_experiment_run(self):
        self.client.experiments.delete(TestWMLClientWithExperiment.experiment_run_uid)

    def test_16_list(self):
        captured_output = io.StringIO()  # Create StringIO object
        sys.stdout = captured_output  # and redirect stdout.
        self.client.repository.list()  # Call function.
        sys.stdout = sys.__stdout__  # Reset redirect.
        self.assertTrue(TestWMLClientWithExperiment.definition_1_uid in captured_output.getvalue())
        self.assertTrue(TestWMLClientWithExperiment.definition_2_uid in captured_output.getvalue())
        # self.assertTrue(TestWMLClientWithExperiment.experiment_uid in captured_output.getvalue())
        self.client.repository.list()  # Just to see values.

    def test_17_delete_experiment(self):
        self.client.repository.delete(TestWMLClientWithExperiment.experiment_uid)

    def test_18_delete_definitions(self):
        self.client.repository.delete(TestWMLClientWithExperiment.definition_1_uid)
        self.client.repository.delete(TestWMLClientWithExperiment.definition_2_uid)

    def test_19_list(self):
        captured_output = io.StringIO()  # Create StringIO object
        sys.stdout = captured_output  # and redirect stdout.
        self.client.repository.list()  # Call function.
        sys.stdout = sys.__stdout__  # Reset redirect.
        self.assertTrue(TestWMLClientWithExperiment.definition_1_uid not in captured_output.getvalue())
        self.assertTrue(TestWMLClientWithExperiment.definition_2_uid not in captured_output.getvalue())
        self.assertTrue(TestWMLClientWithExperiment.experiment_uid not in captured_output.getvalue())
        self.client.repository.list()  # Just to see values.

if __name__ == '__main__':
    unittest.main()
