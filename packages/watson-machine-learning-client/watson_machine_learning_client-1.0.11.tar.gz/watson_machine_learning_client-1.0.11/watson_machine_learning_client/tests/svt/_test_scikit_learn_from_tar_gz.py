import unittest
import os
from watson_machine_learning_client.log_util import get_logger
from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn import preprocessing
from sklearn import svm
from configparser import ConfigParser
import json
from importlib import reload
import site
from watson_machine_learning_client.wml_client_error import WMLClientError
from preparation_and_cleaning import *
from watson_machine_learning_client.utils import SCIKIT_LEARN_FRAMEWORK


class TestWMLClientWithScikitLearn(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithScikitLearn.logger.info("Service Instance: setting up credentials")
        # reload(site)
        self.wml_credentials = get_wml_credentials()
        self.client = get_client()
        self.model_path = os.path.join(os.getcwd(), 'artifacts', 'scikit_model.tar.gz')

    def test_01_service_instance_details(self):
        TestWMLClientWithScikitLearn.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        self.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithScikitLearn.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_publish_model(self):
        global digits
        digits = datasets.load_digits()

        self.logger.info("Publishing scikit-learn model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com",
                       self.client.repository.ModelMetaNames.NAME: "LOCALLY created Digits prediction model",
                       self.client.repository.ModelMetaNames.FRAMEWORK_NAME: SCIKIT_LEARN_FRAMEWORK,
                       self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "0.17"
                       }
        published_model_details = self.client.repository.store_model(model=self.model_path, meta_props=model_props, training_data=digits.data, training_target=digits.target)
        TestWMLClientWithScikitLearn.model_uid = self.client.repository.get_model_uid(published_model_details)
        TestWMLClientWithScikitLearn.model_url = self.client.repository.get_model_url(published_model_details)
        self.logger.info("Published model ID:" + str(TestWMLClientWithScikitLearn.model_uid))
        self.logger.info("Published model URL:" + str(TestWMLClientWithScikitLearn.model_url))
        self.assertIsNotNone(TestWMLClientWithScikitLearn.model_uid)
        self.assertIsNotNone(TestWMLClientWithScikitLearn.model_url)

    def test_03_download_model(self):
        try:
            os.remove('download_test_url')
        except OSError:
            pass

        try:
            file = open('download_test_uid', 'r')
        except IOError:
            file = open('download_test_uid', 'w')
            file.close()

        self.client.repository.download(TestWMLClientWithScikitLearn.model_uid, filename='download_test_url')
        self.assertRaises(WMLClientError, self.client.repository.download, TestWMLClientWithScikitLearn.model_uid, filename='download_test_uid')

    def test_04_publish_model_details(self):
        details = self.client.repository.get_details(self.model_uid)
        TestWMLClientWithScikitLearn.logger.debug("Model details: " + str(details))
        self.assertTrue("LOCALLY created Digits prediction model" in str(details))

        details_all = self.client.repository.get_details()
        TestWMLClientWithScikitLearn.logger.debug("All artifacts details: " + str(details_all))
        self.assertTrue("LOCALLY created Digits prediction model" in str(details_all))

        details_models = self.client.repository.get_model_details()
        TestWMLClientWithScikitLearn.logger.debug("All models details: " + str(details_models))
        self.assertTrue("LOCALLY created Digits prediction model" in str(details_models))

    def test_05_create_deployment(self):
        deployment = self.client.deployments.create(model_uid=self.model_uid, name="Test deployment", asynchronous=False)
        TestWMLClientWithScikitLearn.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithScikitLearn.logger.info("Online deployment: " + str(deployment))
        self.assertTrue(deployment is not None)
        TestWMLClientWithScikitLearn.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithScikitLearn.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertTrue("online" in str(deployment))

    def test_06_get_deployment_details(self):
        deployment_details = self.client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

    def test_07_get_deployment_details_using_uid(self):
        deployment_details = self.client.deployments.get_details(TestWMLClientWithScikitLearn.deployment_uid)
        self.assertIsNotNone(deployment_details)

    def test_08_score(self):
        scoring_data = {'values': [[0.0, 0.0, 5.0, 16.0, 16.0, 3.0, 0.0, 0.0, 0.0, 0.0, 9.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 9.0, 13.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 14.0, 12.0, 0.0, 0.0, 0.0, 0.0, 5.0, 12.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 3.0, 15.0, 15.0, 1.0, 0.0, 0.0], [0.0, 0.0, 6.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 13.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 5.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 16.0, 9.0, 4.0, 1.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0, 16.0, 10.0, 0.0, 0.0, 5.0, 16.0, 11.0, 9.0, 6.0, 2.0]]}
        predictions = self.client.deployments.score(TestWMLClientWithScikitLearn.scoring_url, scoring_data)
        self.assertTrue("prediction" in str(predictions))

    def test_09_delete_deployment(self):
        self.client.deployments.delete(TestWMLClientWithScikitLearn.deployment_uid)

    def test_10_delete_model(self):
        self.client.repository.delete(TestWMLClientWithScikitLearn.model_uid)

if __name__ == '__main__':
    unittest.main()
