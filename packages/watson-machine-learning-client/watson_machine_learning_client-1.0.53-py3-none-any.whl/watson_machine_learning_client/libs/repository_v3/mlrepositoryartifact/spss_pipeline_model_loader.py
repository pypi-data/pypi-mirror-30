################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from repository_v3.mlrepositoryartifact.spss_artifact_loader  import SpssArtifactLoader


class SpssPipelineModelLoader(SpssArtifactLoader):
    """
        Returns Sppss pipeline model instance associated with this model artifact.

        :return: pipeline model
        :rtype: spss.learn.Pipeline
        """
    def load_model(self):
        return(self.model_instance())


    def model_instance(self):
        """
         :return: returns Spss model path
         """
        return self.load()
