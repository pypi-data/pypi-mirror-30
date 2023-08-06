import unittest
import os
import site
import sys
from os.path import join as path_join

SPARK_HOME_PATH = os.environ['SPARK_HOME']
PYSPARK_PATH = str(SPARK_HOME_PATH) + "/python/"
sys.path.insert(1, path_join(PYSPARK_PATH))

from pyspark.sql import SparkSession
from pyspark.ml.feature import OneHotEncoder, StringIndexer, IndexToString, VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline, Model
from importlib import reload
from configparser import ConfigParser
import json
from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *


class TestWMLClientWithSpark(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithSpark.logger.info("Service Instance: setting up credentials")

        self.wml_credentials = get_wml_credentials()
        self.filename = "artifacts/GoSales_Tx_NaiveBayes.csv"
        self.model_name = "SparkMLlibFromObjectPypi Model"
        self.deployment_name = "Test deployment"

        TestWMLClientWithSpark.logger.info("Install fresh client from pypi")
        cmd_uninstall = "pip uninstall -y watson-machine-learning-client"
        cmd_install = "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.python.org/simple/ watson-machine-learning-client"
        self.spark = SparkSession.builder.getOrCreate()
        global df
        df = self.spark.read.load(os.path.join(os.environ['SPARK_HOME'], 'data', 'mllib', 'sample_binary_classification_data.txt'), format='libsvm')

        try:
           import pip
        except ImportError:
            TestWMLClientWithSpark.logger.info("installing pip")
            cmd = "easy_install pip"
            os.system(cmd)
            reload(site)

        execution = os.system(cmd_uninstall)
        TestWMLClientWithSpark.logger.debug(execution)
        reload(site)

        execution_install = os.system(cmd_install)
        TestWMLClientWithSpark.logger.debug(execution_install)
        reload(site)

        self.client = get_client()

    def test_1_service_instance_details(self):
        TestWMLClientWithSpark.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithSpark.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithSpark.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_2_publish_model(self):
        TestWMLClientWithSpark.logger.info("Creating spark model ...")

        df_data = self.spark.read \
            .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
            .option('header', 'true') \
            .option('inferSchema', 'true') \
            .load(self.filename)

        splitted_data = df_data.randomSplit([0.8, 0.18, 0.02], 24)
        train_data = splitted_data[0]
        test_data = splitted_data[1]
        predict_data = splitted_data[2]

        stringIndexer_label = StringIndexer(inputCol="PRODUCT_LINE", outputCol="label").fit(df_data)
        stringIndexer_prof = StringIndexer(inputCol="PROFESSION", outputCol="PROFESSION_IX")
        stringIndexer_gend = StringIndexer(inputCol="GENDER", outputCol="GENDER_IX")
        stringIndexer_mar = StringIndexer(inputCol="MARITAL_STATUS", outputCol="MARITAL_STATUS_IX")

        vectorAssembler_features = VectorAssembler(inputCols=["GENDER_IX", "AGE", "MARITAL_STATUS_IX", "PROFESSION_IX"],
                                                   outputCol="features")
        rf = RandomForestClassifier(labelCol="label", featuresCol="features")
        labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel",
                                       labels=stringIndexer_label.labels)
        pipeline_rf = Pipeline(stages=[stringIndexer_label, stringIndexer_prof, stringIndexer_gend, stringIndexer_mar,
                                       vectorAssembler_features, rf, labelConverter])
        model_rf = pipeline_rf.fit(train_data)

        TestWMLClientWithSpark.logger.info("Publishing spark model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com"}

        published_model = self.client.repository.store_model(model=model_rf, name=self.model_name, meta_props=model_props, training_data=train_data)
        TestWMLClientWithSpark.model_uid = self.client.repository.get_model_uid(published_model)
        TestWMLClientWithSpark.logger.info("Published model ID:" + str(TestWMLClientWithSpark.model_uid))
        self.assertIsNotNone(TestWMLClientWithSpark.model_uid)

    def test_3_publish_model_details(self):
        details = self.client.repository.get_details(self.model_uid)
        TestWMLClientWithSpark.logger.debug("Model details: " + str(details))
        self.assertTrue(self.model_name in str(details))

    def test_4_create_deployment(self):
        deployment = self.client.deployments.create(model_uid=self.model_uid, name="Test deployment")
        TestWMLClientWithSpark.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithSpark.logger.debug("Online deployment: " + str(deployment))
        TestWMLClientWithSpark.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithSpark.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertTrue("online" in str(deployment))

    def test_5_get_deployment_details(self):
        deployment_details = self.client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

    def test_6_score(self):
        scoring_data = {"fields": ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION"], "values": [["M", 23, "Single", "Student"], ["M", 55, "Single", "Executive"]]}
        predictions = self.client.deployments.score(TestWMLClientWithSpark.scoring_url, scoring_data)
        self.assertTrue("prediction" in str(predictions))

    def test_7_delete_deployment(self):
        self.client.deployments.delete(TestWMLClientWithSpark.deployment_uid)

    def test_8_delete_model(self):
        self.client.repository.delete(TestWMLClientWithSpark.model_uid)

if __name__ == '__main__':
    unittest.main()