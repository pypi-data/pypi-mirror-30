import unittest
import os
import sys
from os.path import join as path_join

SPARK_HOME_PATH = os.environ['SPARK_HOME']
PYSPARK_PATH = str(SPARK_HOME_PATH) + "/python/"
sys.path.insert(1, path_join(PYSPARK_PATH))

from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *
from models_preparation import *


class TestWMLClientWithSpark(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithSpark.logger.info("Service Instance: setting up credentials")

        self.wml_credentials = get_wml_credentials()
        self.client = get_client()

        self.model_name = "SparkMLlibFromObjectLocal Model"
        self.deployment_name = "Test deployment"

    def test_1_service_instance_details(self):
        TestWMLClientWithSpark.logger.info("Check client ...")
        self.assertTrue(self.client.__class__.__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithSpark.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithSpark.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_2_publish_model(self):
        TestWMLClientWithSpark.logger.info("Creating spark model ...")

        model_data = create_spark_mllib_model_data()

        TestWMLClientWithSpark.logger.info("Publishing spark model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com",
                       self.client.repository.ModelMetaNames.NAME: self.model_name,
                       self.client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: {
                            "name": "test",
                            "type": "s3",
                            "connection": {
                                "access_key_id": "xxx",
                                "secret_access_key": "xxx",
                                "endpoint_url": "https://xxx.ibm.com"
                            },
                            "source": {
                                "bucket": "xxx",
                                "key": "xxx"
                            }
                        },
                       self.client.repository.ModelMetaNames.EVALUATION_METHOD: "multiclass",
                       self.client.repository.ModelMetaNames.EVALUATION_METRICS: [
                           {
                               "name": "accuracy",
                               "value": 0.64,
                               "threshold": 0.8
                           }
                       ]
                    }

        TestWMLClientWithSpark.logger.info(model_data['pipeline'])
        TestWMLClientWithSpark.logger.info(type(model_data['pipeline']))

        published_model = self.client.repository.store_model(model=model_data['model'], meta_props=model_props, training_data=model_data['training_data'], pipeline=model_data['pipeline'])
        TestWMLClientWithSpark.model_uid = self.client.repository.get_model_uid(published_model)
        TestWMLClientWithSpark.logger.info("Published model ID:" + str(TestWMLClientWithSpark.model_uid))
        self.assertIsNotNone(TestWMLClientWithSpark.model_uid)

    def test_3_get_details(self):
        TestWMLClientWithSpark.logger.info("Get details")
        details = self.client.repository.get_details(self.model_uid)
        TestWMLClientWithSpark.logger.debug("Model details: " + str(details))
        self.assertTrue(self.model_name in str(details))

        import requests

        response = requests.get(
            details['entity']['evaluation_metrics_url'],
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.client.wml_token}
        )

        self.assertTrue("0.64" in str(response.text))

    def test_4_create_deployment(self):
        TestWMLClientWithSpark.logger.info("Create deployment")
        deployment = self.client.deployments.create(model_uid=self.model_uid, name=self.deployment_name, asynchronous=False)
        TestWMLClientWithSpark.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithSpark.logger.debug("Online deployment: " + str(deployment))
        TestWMLClientWithSpark.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithSpark.logger.debug("Scoring url: {}".format(TestWMLClientWithSpark.scoring_url))
        TestWMLClientWithSpark.deployment_uid = self.client.deployments.get_uid(deployment)
        TestWMLClientWithSpark.logger.debug("Deployment uid: {}".format(TestWMLClientWithSpark.deployment_uid))
        self.assertTrue("online" in str(deployment))

    def test_5_get_deployment_details(self):
        TestWMLClientWithSpark.logger.info("Get deployment details")
        deployment_details = self.client.deployments.get_details()
        TestWMLClientWithSpark.logger.debug("Deployment details: {}".format(deployment_details))
        self.assertTrue(self.deployment_name in str(deployment_details))

    def test_6_score(self):
        TestWMLClientWithSpark.logger.info("Score the model")
        scoring_data = {"fields": ["GENDER","AGE","MARITAL_STATUS","PROFESSION"],"values": [["M",23,"Single","Student"],["M",55,"Single","Executive"]]}
        predictions = self.client.deployments.score(TestWMLClientWithSpark.scoring_url, scoring_data)
        TestWMLClientWithSpark.logger.debug("Predictions: {}".format(predictions))
        self.assertTrue("prediction" in str(predictions))

    def test_7_delete_deployment(self):
        TestWMLClientWithSpark.logger.info("Delete deployment")
        self.client.deployments.delete(TestWMLClientWithSpark.deployment_uid)

    def test_8_delete_model(self):
        TestWMLClientWithSpark.logger.info("Delete model")
        self.client.repository.delete(TestWMLClientWithSpark.model_uid)


if __name__ == '__main__':
    unittest.main()
