#!/usr/bin/env python

import os
import logging
from pyspark.sql import *
from .aws import S3


class Spark(object):
    def __init__(self, spark_url='local', app='PanameraApp', path=None, is_remote=False, bucket=None):
        """
        Constructor
        :param spark_url: sets the Spark master URL to connect to, such as 'local' to run locally, or 'spark://master:7077' to run on a Spark standalone cluster
        :param app = spark application name
        :param path: absolute local path of the file or S3 prefix of the file [String]
        :param is_remote: indicates if the path informed is local or remote (s3 file) [Boolean]
        :param bucket: bucket name [String]
        """
        self._logger = logging.getLogger(__name__)
        self._spark_url = spark_url
        self._app = app
        self._file_path = path
        self._tmp_file = None
        try:
            if path:
                self._file_name = (self._file_path.split(os.sep)[-1]).split('.')[0]
                self._file_format = path.split('.')[-1].lower()
                self._file_name_full = self._file_name + '.' + self._file_format
                if is_remote:
                    self._file_source = 's3'
                    self._bucket = bucket

                    if self._file_format != 'parquet':
                        raise Exception('File format for remote files stored in S3 must be parquet')

                    if not bucket:
                        raise Exception('Bucket must be informed for remote files')

                    self._s3_client = S3(bucket=bucket, profile='reservoir')
                    if not self._s3_client.exists(self._file_path):
                        raise Exception('File {} does not exist in S3 bucket {}'.format(self._file_path, self._bucket))

                    # Cleaning tmp file
                    tmp_file = os.path.join('tmp', self._file_name_full)
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)

                else:
                    self._file_source = 'file'
                    self._bucket = ''

                # Spark session
                self._session = SparkSession.builder \
                    .master(self._spark_url) \
                    .appName(self._app) \
                    .enableHiveSupport() \
                    .getOrCreate()
                self._dataframe = None

                self._file_full_path = self._file_source + '://' + os.path.join(self._bucket, self._file_path)

            else:
                self._bucket = None
                self._file_type = None
                self._file_name = None
                self._file_format = None
                self._file_full_path = None

        except Exception as ex:
            print(repr(ex))

    def set_file(self, path, is_remote=False, bucket=None):
        """
        Set file path (remote or local file)
        :param path: absolute local path of the file or S3 prefix of the file [String]
        :param is_remote: indicates if the path informed is local or remote (s3 file) [Boolean]
        :param bucket: bucket name [String]
        :return: None
        """
        self._file_name = (self._file_path.split(os.sep)[-1]).split('.')[0]
        self._file_format = path.split('.')[-1].lower()
        self._file_name_full = self._file_name + '.' + self._file_format

        if is_remote:
            self._file_source = 's3'
            if not bucket:
                raise Exception('Bucket must be informed for remote files')
            else:
                self._bucket = bucket
        else:
            self._file_source = 'file'
            self._bucket = ''

        self._file_full_path = self._file_source + '://' + os.path.join(self._bucket, self._file_path)

    def read(self):
        """
        Read file local or remote
        :return: dataframe with data loaded from file [Dataframe]
        """
        if not self._file_full_path:
            raise Exception('No file informed. Use set_file method for this purpose and run it again')

        try:
            if self._file_source == 's3':
                tmp_file = os.path.join('tmp', self._file_name_full)
                if not os.path.exists(tmp_file):
                    local_path = self._s3_client.download(prefix=self._file_path, local_path='/tmp')[0]
                else:
                    local_path = tmp_file
                self._tmp_file = local_path

            else:
                local_path = self._file_full_path

            self._dataframe = self._session.read.load(local_path, format=self._file_format)

            return self._dataframe
        except Exception as ex:
            print(repr(ex))

    def get_columns(self):
        """
        Get dataframe columns
        :return: list with all columns [List]
        """
        return self._dataframe.columns

    def remove_temporal_file(self):
        """
        Remove temporal file created (if exists)
        :return: None
        """
        if self._tmp_file:
            os.remove(self._tmp_file)
            self._tmp_file = None

    def __repr__(self):
        return str({'AppName': self._app, 'MasterURL': self._spark_url, 'File Path': self._file_full_path})

