from repository_v3.mlrepository import ModelArtifact

class SpssModelArtifact(ModelArtifact):
    """
    Class representing Spps model artifact
    """
    def __init__(self, uid, name, meta_props):
        """
        Constructor for Spss model artifact
        :param uid: unique id for Spss model artifact
        :param name: name of the model
        :param metaprops: properties of the model and model artifact
        """
        super(SpssModelArtifact, self).__init__(uid, name, meta_props)