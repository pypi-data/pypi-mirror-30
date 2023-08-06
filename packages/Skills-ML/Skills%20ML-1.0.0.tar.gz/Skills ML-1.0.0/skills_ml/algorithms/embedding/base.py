"""Embedding model class interfacing with with gensim and tensorflow"""
import os
import logging
import json
import tempfile
import numpy as np
import boto

from gensim.models import Doc2Vec, Word2Vec

from skills_utils.s3 import download, split_s3_path, list_files

S3_PATH_EMBEDDING_MODEL = 'open-skills-private/model_cache/embedding/'

class Word2VecModel(object):
    """The Word2VecModel Object is a base object which specifies which word-embeding model.

    Example:
    ```
    from airflow.hooks import S3Hook
    from skills_ml.algorithms.embedding.base import Word2VecModel

    s3_conn = S3Hook().get_conn()
    word2vec_model = Word2VecModel(s3_conn=s3_conn)
    ```
    """
    def __init__(self, model_name='word2vec_gensim_2017-07-14T11:32:00.997426',
        model=None, s3_conn=None, s3_path=S3_PATH_EMBEDDING_MODEL):
        """
        Attributes:
            model_name (str): name of the model to be used.
            s3_path (str): the path of the model on S3.
            s3_conn (:obj: `boto.s3.connection.S3Connection`): the boto object to connect to S3.
            files (:obj: `list` of (str)): model files need to be downloaded/loaded.
            model (:obj: `gensim.models.doc2vec.Doc2Vec`): gensim doc2vec model.
            lookup (dict): lookup table for mapping each jobposting index to soc code.
        """
        self.model_name = model_name
        self.s3_path = s3_path + self.model_name
        self.s3_conn = s3_conn
        self.model = self._load_model() if model == None else model

    def _load_model(self):
        """The method to download the model from S3 and load to the memory.

        Returns:
            gensim.models.doc2vec.Doc2Vec: The word-embedding model object.
        """
        files  = list_files(self.s3_conn, self.s3_path)
        with tempfile.TemporaryDirectory() as td:
            for f in files:
                filepath = os.path.join(td, f)
                if not os.path.exists(filepath):
                    logging.info('calling download from %s to %s', self.s3_path + f, filepath)
                    download(self.s3_conn, filepath, os.path.join(self.s3_path, f))
            model = Word2Vec.load(os.path.join(td, self.model_name+".model"))

            return model


class Doc2VecModel(object):
    """The Doc2VecModel Object is a base object which specifies which word-embeding model.

    Example:
    ```
    from airflow.hooks import S3Hook
    from skills_ml.algorithms.embedding.base import Doc2VecModel

    s3_conn = S3Hook().get_conn()
    doc2vec_model = Doc2VecModel(s3_conn=s3_conn)
    ```
    """
    def __init__(self, model_name='doc2vec_2017-07-14T11:32:00.997426',
        lookup=None, model=None, s3_conn=None, s3_path=S3_PATH_EMBEDDING_MODEL):
        """
        Attributes:
            model_name (str): name of the model to be used.
            lookup_name (str): name of the lookup file
            s3_path (str): the path of the model on S3.
            s3_conn (:obj: `boto.s3.connection.S3Connection`): the boto object to connect to S3.
            model (:obj: `gensim.models.doc2vec.Doc2Vec`): gensim doc2vec model.
            lookup (dict): lookup table for mapping each jobposting index to soc code.
            training_data (np.ndarray): a document vector array where each row is a document vector.
            target (np.ndarray): a label array.
        """
        self.model_name = model_name
        self.lookup_name = 'lookup_' + self.model_name + '.json'
        self.s3_path = s3_path + self.model_name
        self.s3_conn = s3_conn
        self.model = self._load_model() if model == None else model
        self.lookup = self._load_lookup() if lookup == None else lookup
        self.training_data = self.model.docvecs.doctag_syn0 if hasattr(self.model, 'docvecs') else None
        self.target = self._create_target_data() if hasattr(self.model, 'docvecs') else None

    def _load_model(self):
        """The method to download the model from S3 and load to the memory.

        Returns:
            gensim.models.doc2vec.Doc2Vec: The word-embedding model object.
        """
        files  = list_files(self.s3_conn, self.s3_path)
        with tempfile.TemporaryDirectory() as td:
            for f in files:
                filepath = os.path.join(td, f)
                if not os.path.exists(filepath):
                    logging.info('calling download from %s to %s', self.s3_path + f, filepath)
                    download(self.s3_conn, filepath, os.path.join(self.s3_path, f))
            model = Doc2Vec.load(os.path.join(td, self.model_name+".model"))

            return model

    def _load_lookup(self):
        """The method to download the lookup dictionary from S3 and load to the memory.

        Returns:
            dict: a lookup table for mapping gensim index to soc code.
        """
        with tempfile.TemporaryDirectory() as td:
            filepath = os.path.join(td, self.lookup_name)
            logging.info('calling download from %s to %s', self.s3_path + self.lookup_name, filepath)
            try:
                download(self.s3_conn, filepath, os.path.join(self.s3_path, self.lookup_name))
                with open(filepath, 'r') as handle:
                    lookup = json.load(handle)
            except boto.exception.S3ResponseError:
                lookup = None

            return lookup

    @property
    def target_data(self):
        return self._create_target_data

    def _create_target_data(self):
        """To create a label array by mapping each doc vector to the lookup table.

        Returns:
            np.ndarray: label array.
        """
        y = []
        for i in range(len(self.training_data)):
            y.append(self.lookup[str(self.model.docvecs.index_to_doctag(i))])

        return np.array(y)
