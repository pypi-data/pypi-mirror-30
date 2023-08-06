#!/usr/bin/env python

import os
import logging
from pyspark.sql import *
from pypanabi.aws import S3
from pyspark.conf import SparkConf


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
        if path:
            self._file_name = (self._file_path.split(os.sep)[-1]).split('.')[0]
            self._file_format = path.split('.')[-1].lower()
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
            else:
                self._file_source = 'file'
                self._bucket = ''

            self._file_full_path = self._file_source + '://' + os.path.join(self._bucket, self._file_path)

        else:
            self._bucket = None
            self._file_type = None
            self._file_name = None
            self._file_format = None
            self._file_full_path = None

        try:
            # Spark session
            self._session = SparkSession.builder\
                                        .master(self._spark_url)\
                                        .appName(self._app)\
                                        .enableHiveSupport()\
                                        .getOrCreate()
            self._dataframe = None
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
        if is_remote:
            self._file_source = 's3'
            if not bucket:
                raise Exception('Bucket must be informed for remote files')
            else:
                self._bucket = bucket
                self._file_full_path = 's3://' + os.path.join(self._bucket, self._file_path)
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
                self._dataframe = self._session.read.parquet(self._file_full_path)
            else:
                self._dataframe = self._session.read.load(self._file_full_path, format=self._file_format)
            return self._dataframe
        except Exception as ex:
            print(repr(ex))

    def get_dataframe(self):
        """
        Get Dataframe
        :return: dataframe [Dataframe]
        """
        return self._dataframe

    def show_dataframe(self):
        """
        Show dataframe
        :return: data stored in the dataframe [String]
        """
        self._dataframe.show()

    def get_columns(self):
        """
        Get dataframe columns
        :return: list with all columns [List]
        """
        return self._dataframe.columns

    def __repr__(self):
        return str({'AppName': self._app, 'MasterURL': self._spark_url, 'File Path': self._file_full_path})

