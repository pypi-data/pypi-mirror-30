import unittest
import os
import site
import xgboost as xgb
from importlib import reload
from configparser import ConfigParser
import json
from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *


class TestWMLClientWithXGBoost(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithXGBoost.logger.info("Service Instance: setting up credentials")
        self.wml_credentials = get_wml_credentials()

        TestWMLClientWithXGBoost.logger.info("Install fresh client from pypi")
        cmd_uninstall = "pip uninstall -y watson-machine-learning-client"
        cmd_install = "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.python.org/simple/ watson-machine-learning-client"

        try:
           import pip
        except ImportError:
            TestWMLClientWithXGBoost.logger.info("installing pip")
            cmd = "easy_install pip"
            os.system(cmd)
            reload(site)

        execution = os.system(cmd_uninstall)
        TestWMLClientWithXGBoost.logger.debug(execution)
        reload(site)

        execution_install = os.system(cmd_install)
        TestWMLClientWithXGBoost.logger.debug(execution_install)
        reload(site)

        self.client = get_client()

    def test_1_service_instance_details(self):
        TestWMLClientWithXGBoost.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithXGBoost.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()

        TestWMLClientWithXGBoost.logger.debug(details)
        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_2_publish_model(self):
        TestWMLClientWithXGBoost.logger.info("Creating xgboost model ...")

        global agaricus
        agaricus = xgb.DMatrix(os.path.join('artifacts', 'agaricus.txt.train'))
        param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}
        num_round = 2

        global model
        model = xgb.train(params=param, dtrain=agaricus, num_boost_round=num_round)
        predicted = model.predict(agaricus.slice(range(5)))

        TestWMLClientWithXGBoost.logger.info("Predicted values:")
        TestWMLClientWithXGBoost.logger.debug(predicted)

        self.assertIsNotNone(predicted)

        TestWMLClientWithXGBoost.logger.info("Publishing xgboost model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com"}
        model_name = "LOCALLY created agaricus prediction model"
        published_model = self.client.repository.store_model(model=model, name=model_name, meta_props=model_props)
        TestWMLClientWithXGBoost.model_uid = self.client.repository.get_model_uid(published_model)
        TestWMLClientWithXGBoost.logger.info("Published model ID:" + str(TestWMLClientWithXGBoost.model_uid))
        self.assertIsNotNone(TestWMLClientWithXGBoost.model_uid)

    def test_3_publish_model_details(self):
        TestWMLClientWithXGBoost.logger.info("Get model details ...")
        details = self.client.repository.get_details(self.model_uid)

        TestWMLClientWithXGBoost.logger.debug("Model details: " + str(details))
        self.assertTrue("LOCALLY created agaricus prediction model" in str(details))

    def test_4_create_deployment(self):
        TestWMLClientWithXGBoost.logger.info("Create deployment ...")
        deployment = self.client.deployments.create(self.model_uid, "Test deployment")

        TestWMLClientWithXGBoost.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithXGBoost.logger.debug("Online deployment: " + str(deployment))
        TestWMLClientWithXGBoost.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithXGBoost.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertTrue("online" in str(deployment))

    def test_5_get_deployment_details(self):
        TestWMLClientWithXGBoost.logger.info("Get deployment details ...")
        deployment_details = self.client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

    def test_6_score(self):
        TestWMLClientWithXGBoost.logger.info("Score deployed model ...")
        scoring_data = {'values': [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0,
                                    0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                    1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
                                    0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0,
                                    1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                                    0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
                                    0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]]}
        predictions = self.client.deployments.score(scoring_url=TestWMLClientWithXGBoost.scoring_url, payload=scoring_data)
        TestWMLClientWithXGBoost.logger.debug("Prediction: " + str(predictions))
        self.assertTrue("prediction" in predictions["fields"] or "probability" in predictions["fields"])

    def test_7_delete_deployment(self):
        TestWMLClientWithXGBoost.logger.info("Delete model deployment ...")
        self.client.deployments.delete(TestWMLClientWithXGBoost.deployment_uid)

    def test_8_delete_model(self):
        TestWMLClientWithXGBoost.logger.info("Delete model ...")
        self.client.repository.delete(TestWMLClientWithXGBoost.model_uid)

if __name__ == '__main__':
    unittest.main()