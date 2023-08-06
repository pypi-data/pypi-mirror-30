################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


import os
import shutil
import logging

from repository_v3.mlrepository.artifact_reader import ArtifactReader
from repository_v3.mlrepositoryartifact.version_helper import ScikitModelBinary
from repository_v3.util.compression_util import CompressionUtil
from repository_v3.util.unique_id_gen import uid_generate
from repository_v3.util.library_imports import LibraryChecker
from repository_v3.base_constants import *


logger = logging.getLogger('SpssPipelineReader')


class SpssPipelineReader(ArtifactReader):
    def __init__(self, spss_pipeline):
        self.archive_path = None
        self.spss_pipeline = spss_pipeline
        self.type_name = 'model'

    def read(self):
        return self._open_stream()

    def close(self):
        pass

    def _open_stream(self):
        self.archive_path = self.spss_pipeline
        return open(self.archive_path, 'rb')

