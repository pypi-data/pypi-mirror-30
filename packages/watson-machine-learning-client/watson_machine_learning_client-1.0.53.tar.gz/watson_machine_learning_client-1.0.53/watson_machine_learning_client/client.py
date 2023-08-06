################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

import sys
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.utils import version
from os.path import join as path_join
import pkg_resources

try:
    wml_location = pkg_resources.get_distribution("watson-machine-learning-client").location
    sys.path.insert(1, path_join(wml_location, 'watson_machine_learning_client', 'libs'))
except pkg_resources.DistributionNotFound:
    pass

from repository_v3.mlrepositoryclient import MLRepositoryClient
from watson_machine_learning_client.learning_system import LearningSystem
from watson_machine_learning_client.experiments import Experiments
from watson_machine_learning_client.repository import Repository
from watson_machine_learning_client.instance import ServiceInstance
from watson_machine_learning_client.deployments import Deployments
from watson_machine_learning_client.training import Training
from watson_machine_learning_client.utils import get_ml_token
from watson_machine_learning_client.wml_client_error import NoWMLCredentialsProvided

'''
.. module:: WatsonMachineLearningAPIClient
   :platform: Unix, Windows
   :synopsis: Watson Machine Learning API Client.

.. moduleauthor:: IBM
'''


class WatsonMachineLearningAPIClient:

    def __init__(self, wml_credentials):
        self._logger = get_logger(__name__)
        if wml_credentials is None:
            raise NoWMLCredentialsProvided()
        self.wml_credentials = wml_credentials
        self.wml_token, self._ml_repository_client = self._connect()
        self.service_instance = ServiceInstance(self.wml_credentials, self.wml_token)
        self.instance_details = self.service_instance.get_details()
        self.repository = Repository(self, self._ml_repository_client)
        self.deployments = Deployments(self)
        self.experiments = Experiments(self)
        self.learning_system = LearningSystem(self)
        self.training = Training(self)
        self._logger.info(u'Client successfully initialized')
        self.version = version()

    def _connect(self):
        if self.wml_credentials is not None:
            _ml_repository_client = MLRepositoryClient(self.wml_credentials[u'url'])

            _ml_repository_client.authorize(self.wml_credentials[u'username'],
                                           self.wml_credentials[u'password'])

            _ml_repository_client._add_header('X-WML-User-Client', 'PythonClient')

            wml_token = get_ml_token(self.wml_credentials)
            self._logger.info(u'Successfully prepared token: ' + wml_token)
            return wml_token, _ml_repository_client
        else:
            raise NoWMLCredentialsProvided()

    def _refresh_token(self):
        self.wml_token, self._ml_repository_client = self._connect()

    # @staticmethod
    # def _version():
    #     try:
    #         version = pkg_resources.get_distribution("watson-machine-learning-client").version
    #     except pkg_resources.DistributionNotFound:
    #         version = u'0.0.1-local'
    #
    #     return version
