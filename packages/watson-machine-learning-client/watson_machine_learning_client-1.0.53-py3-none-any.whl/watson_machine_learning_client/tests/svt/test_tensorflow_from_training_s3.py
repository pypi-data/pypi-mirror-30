import unittest
import os
from configparser import ConfigParser
import json
from importlib import reload
import site
import time
import swiftclient.client as swiftclient
import boto3
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import ApiRequestFailure, WMLClientError
from preparation_and_cleaning import *


class TestWMLClientWithTensorflow(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    definition_uid = None
    trained_model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithTensorflow.logger.info("Service Instance: setting up credentials")
        self.wml_credentials = get_wml_credentials()
        # reload(site)
        self.client = get_client()
        self.cos_resource = get_cos_resource()
        prepare_cos(self.cos_resource)

    @classmethod
    def tearDownClass(self):
        clean_cos(self.cos_resource)

    def test_01_service_instance_details(self):
        TestWMLClientWithTensorflow.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithTensorflow.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithTensorflow.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    # def test_02_models_supported_frameworks(self):
    #     print("Get supported frameworks ...")
    #     frameworks = self.client.training.get_frameworks()
    #     print("Frameworks: " + str(frameworks))
    #     self.assertIsNotNone(frameworks)
    #     self.assertTrue("tensorflow" in str(frameworks))

    def test_02_get_trained_models(self):
        TestWMLClientWithTensorflow.logger.info("Get trained models details...")
        models = self.client.training.get_details()
        TestWMLClientWithTensorflow.logger.debug("Models: " + str(models))
        self.assertIsNotNone(models)

    def test_03_save_definition(self):
        TestWMLClientWithTensorflow.logger.info("Save model definition ...")

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
        TestWMLClientWithTensorflow.definition_uid = self.client.repository.get_definition_uid(definition_details)
        TestWMLClientWithTensorflow.logger.info("Saved model definition uid: " + str(TestWMLClientWithTensorflow.definition_uid))

    def test_04_get_definition_details(self):
        print("Getting definition details ...")
        details = self.client.repository.get_definition_details()
        print(details)
        self.assertTrue('my_training_definition' in str(details))

    def test_05_train_using_interactive_mode_s3(self):
        TestWMLClientWithTensorflow.logger.info("Train TensorFlow model ...")

        self.client.training.ConfigurationMetaNames.show()

        training_configuration_dict = {
            self.client.training.ConfigurationMetaNames.NAME: "Hand-written Digit Recognition",
            self.client.training.ConfigurationMetaNames.AUTHOR_NAME: "John Smith",
            self.client.training.ConfigurationMetaNames.AUTHOR_EMAIL: "JohnSmith@js.com",
            self.client.training.ConfigurationMetaNames.DESCRIPTION: "Hand-written Digit Recognition training",
            self.client.training.ConfigurationMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.training.ConfigurationMetaNames.FRAMEWORK_VERSION: "1.2-py3",
            self.client.training.ConfigurationMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20",
            self.client.training.ConfigurationMetaNames.EXECUTION_RESOURCE_SIZE: "small",
            self.client.training.ConfigurationMetaNames.TRAINING_DATA_REFERENCE: {
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
            self.client.training.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE: {
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
        }

        training_details = self.client.training.run(definition_uid=TestWMLClientWithTensorflow.definition_uid, meta_props=training_configuration_dict, asynchronous=False)
        TestWMLClientWithTensorflow.trained_model_uid = self.client.training.get_run_uid(training_details)
        TestWMLClientWithTensorflow.logger.info(
            "Trained model guid: " + TestWMLClientWithTensorflow.trained_model_uid)
        self.assertTrue('training' in TestWMLClientWithTensorflow.trained_model_uid)

    def test_06_get_trained_status(self):
        status = self.client.training.get_status(TestWMLClientWithTensorflow.trained_model_uid)
        TestWMLClientWithTensorflow.logger.info("Training status: " + str(status))
        self.assertTrue('state' in status)

    def test_07_get_trained_details(self):
        details = self.client.training.get_details(TestWMLClientWithTensorflow.trained_model_uid)
        state = details['entity']['status']['state']

        TestWMLClientWithTensorflow.logger.info("Training state:" + state)
        TestWMLClientWithTensorflow.logger.debug("Training details: " + str(details))

        self.assertTrue('state' in str(details))

        TestWMLClientWithTensorflow.logger.info('Getting details DONE.')
        self.assertTrue('completed' in state)

    def test_08_save_trained_model_in_repository(self):
        TestWMLClientWithTensorflow.logger.info("Saving trained model in repo ...")
        saved_model_details = self.client.repository.store_model(TestWMLClientWithTensorflow.trained_model_uid, "My supercool TF sample model")
        TestWMLClientWithTensorflow.model_uid = saved_model_details['entity']['ml_asset_guid']
        print(saved_model_details)
        self.assertIsNotNone(saved_model_details)

    def test_09_check_meta_names(self):
        author_name = self.client.repository.DefinitionMetaNames.AUTHOR_NAME
        self.assertTrue(author_name == 'author_name')

        author_name2 = self.client.training.ConfigurationMetaNames.AUTHOR_NAME
        self.assertTrue(author_name2 == 'author_name')

    def test_10_get_trained_models_table(self):
        self.client.training.list()

    def test_11_delete_train_run(self):
        deleted = self.client.training.delete(TestWMLClientWithTensorflow.trained_model_uid)
        print(str(deleted))

        trained_models = self.client.training.get_details()
        self.assertTrue(str(TestWMLClientWithTensorflow.trained_model_uid) not in str(trained_models))

    def test_12_check_if_train_run_deleted(self):
        TestWMLClientWithTensorflow.logger.info("Checking if model has been deleted ...")
        self.assertRaises(WMLClientError, self.client.training.get_status, TestWMLClientWithTensorflow.trained_model_uid)
        self.assertRaises(WMLClientError, self.client.training.get_details, TestWMLClientWithTensorflow.trained_model_uid)
        self.assertRaises(ApiRequestFailure, self.client.repository.store_model, TestWMLClientWithTensorflow.trained_model_uid, "My supercool TF sample model")


    def test_13_create_deployment(self):
        deployment_details = self.client.deployments.create(model_uid=TestWMLClientWithTensorflow.model_uid, name="Test deployment")
        TestWMLClientWithTensorflow.logger.debug("Deployment details: " + str(deployment_details))
        TestWMLClientWithTensorflow.deployment_uid = self.client.deployments.get_deployment_uid(deployment_details)
        TestWMLClientWithTensorflow.scoring_url = self.client.deployments.get_scoring_url(deployment_details)
        self.assertTrue('online' in str(TestWMLClientWithTensorflow.scoring_url))

    def test_14_scoring(self):
        scoring_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 18, 18, 18,
                                 126, 136, 175, 26, 166, 255, 247, 127, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 30, 36, 94, 154, 170, 253,
                                 253, 253, 253, 253, 225, 172, 253, 242, 195, 64, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 49, 238, 253, 253, 253,
                                 253, 253, 253, 253, 253, 251, 93, 82, 82, 56, 39, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 219, 253,
                                 253, 253, 253, 253, 198, 182, 247, 241, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 80, 156, 107, 253, 253, 205, 11, 0, 43, 154, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 14, 1, 154, 253, 90, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 139, 253, 190, 2, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 190, 253, 70,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 35,
                                 241, 225, 160, 108, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 81, 240, 253, 253, 119, 25, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 45, 186, 253, 253, 150, 27, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 16, 93, 252, 253, 187,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 249,
                                 253, 249, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 46, 130,
                                 183, 253, 253, 207, 2, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 39, 148,
                                 229, 253, 253, 253, 250, 182, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 114,
                                 221, 253, 253, 253, 253, 201, 78, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 66,
                                 213, 253, 253, 253, 253, 198, 81, 2, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 171,
                                 219, 253, 253, 253, 253, 195, 80, 9, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 55, 172,
                                 226, 253, 253, 253, 253, 244, 133, 11, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 136, 253, 253, 253, 212, 135, 132, 16, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0]

        scoring_payload = {'inputs': [scoring_data, scoring_data]}
        scores = self.client.deployments.score(scoring_url=TestWMLClientWithTensorflow.scoring_url, payload=scoring_payload)
        self.assertIsNotNone(scores)

    def test_15_delete_deployment(self):
        self.client.deployments.delete(TestWMLClientWithTensorflow.deployment_uid)

    def test_16_delete_model(self):
        self.client.repository.delete(TestWMLClientWithTensorflow.model_uid)

    def test_17_delete_definition(self):
        self.client.repository.delete(TestWMLClientWithTensorflow.definition_uid)

    def test_18_clenup_s3(self):
        TestWMLClientWithTensorflow.logger.info("Cleaning aws S3...")

        endpoint = 'http://s3-api.us-geo.objectstorage.softlayer.net/'
        cos = boto3.resource('s3', endpoint_url=endpoint, aws_access_key_id='zfho4HT7pUIStZvSkDsl',
                             aws_secret_access_key='21q66Vvxkhr4uPDacTf8F9fnzMjSUIzsZRtxrYbx')

        TestWMLClientWithTensorflow.logger.info("List of file to clean: ")
        for bucket in cos.buckets.all():
            if bucket.name == 'wml-dev-results':
                for obj in bucket.objects.all():
                    if TestWMLClientWithTensorflow.trained_model_uid in obj.key:
                        print("  {}".format(obj.key))
                        obj.delete()

        files = []
        for bucket in cos.buckets.all():
            if bucket.name == 'wml-dev-results':
                for obj in bucket.objects.all():
                    if TestWMLClientWithTensorflow.trained_model_uid in obj.key:
                        files.append(obj)

        print(len(files))

        self.assertEqual(len(files), 0)


if __name__ == '__main__':
    unittest.main()
