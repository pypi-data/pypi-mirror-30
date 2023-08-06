import unittest
import os
import site
from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn import preprocessing
from sklearn import svm
from importlib import reload
from configparser import ConfigParser
import json
from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *


class TestWMLClientWithScikitLearn(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithScikitLearn.logger.info("Service Instance: setting up credentials")

        self.wml_credentials = get_wml_credentials()

        TestWMLClientWithScikitLearn.logger.info("Install fresh client from pypi")
        cmd_uninstall = "pip uninstall -y watson-machine-learning-client"
        cmd_install = "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.python.org/simple/ watson-machine-learning-client"

        try:
           import pip
        except ImportError:
            TestWMLClientWithScikitLearn.logger.info("installing pip")
            cmd = "easy_install pip"
            os.system(cmd)
            reload(site)

        execution = os.system(cmd_uninstall)
        TestWMLClientWithScikitLearn.logger.debug(execution)
        reload(site)

        execution_install = os.system(cmd_install)
        TestWMLClientWithScikitLearn.logger.debug(execution_install)
        reload(site)

        self.client = get_client()

    def test_1_service_instance_details(self):
        TestWMLClientWithScikitLearn.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithScikitLearn.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithScikitLearn.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_2_publish_model(self):
        TestWMLClientWithScikitLearn.logger.info("Creating scikit-learn model ...")
        global digits
        digits = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        global model
        model = pipeline.fit(digits.data, digits.target)
        predicted = model.predict(digits.data[1: 10])

        TestWMLClientWithScikitLearn.logger.debug(predicted)
        self.assertIsNotNone(predicted)

        TestWMLClientWithScikitLearn.logger.info("Publishing scikit-learn model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com"}
        model_name = "LOCALLY created Digits prediction model"
        published_model = self.client.repository.store_model(model=model, name=model_name, meta_props=model_props, training_data=digits.data, training_target=digits.target)
        TestWMLClientWithScikitLearn.model_uid = self.client.repository.get_model_uid(published_model)
        TestWMLClientWithScikitLearn.logger.info("Published model ID:" + str(TestWMLClientWithScikitLearn.model_uid))
        self.assertIsNotNone(TestWMLClientWithScikitLearn.model_uid)

    def test_3_publish_model_details(self):
        details = self.client.repository.get_details(self.model_uid)
        TestWMLClientWithScikitLearn.logger.debug("Model details: " + str(details))
        self.assertTrue("LOCALLY created Digits prediction model" in str(details))

        details_all = self.client.repository.get_details()
        TestWMLClientWithScikitLearn.logger.debug("All artifacts details: " + str(details_all))
        self.assertTrue("LOCALLY created Digits prediction model" in str(details_all))

        details_models = self.client.repository.get_model_details()
        TestWMLClientWithScikitLearn.logger.debug("All models details: " + str(details_models))
        self.assertTrue("LOCALLY created Digits prediction model" in str(details_models))

    def test_4_create_deployment(self):
        deployment = self.client.deployments.create(model_uid=self.model_uid, name="Test deployment")
        TestWMLClientWithScikitLearn.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithScikitLearn.logger.info("Online deployment: " + str(deployment))
        TestWMLClientWithScikitLearn.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithScikitLearn.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertTrue("online" in str(deployment))

    def test_5_get_deployment_details(self):
        deployment_details = self.client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

    def test_6_score(self):
        scoring_data = {'values': [[0.0, 0.0, 5.0, 16.0, 16.0, 3.0, 0.0, 0.0, 0.0, 0.0, 9.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 9.0, 13.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 14.0, 12.0, 0.0, 0.0, 0.0, 0.0, 5.0, 12.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 3.0, 15.0, 15.0, 1.0, 0.0, 0.0], [0.0, 0.0, 6.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 13.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 5.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 16.0, 9.0, 4.0, 1.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0, 16.0, 10.0, 0.0, 0.0, 5.0, 16.0, 11.0, 9.0, 6.0, 2.0]]}
        predictions = self.client.deployments.score(TestWMLClientWithScikitLearn.scoring_url, scoring_data)
        self.assertTrue("prediction" in str(predictions))

    def test_7_delete_deployment(self):
        self.client.deployments.delete(TestWMLClientWithScikitLearn.deployment_uid)

    def test_8_delete_model(self):
        self.client.repository.delete(TestWMLClientWithScikitLearn.model_uid)

if __name__ == '__main__':
    unittest.main()