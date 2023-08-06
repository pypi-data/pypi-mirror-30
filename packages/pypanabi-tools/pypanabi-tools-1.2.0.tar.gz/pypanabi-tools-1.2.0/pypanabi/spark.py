#!/usr/bin/env python

import os
from pyspark.sql import *
from .aws import S3
from pandas.io.json import json_normalize


class Spark(object):
    def __init__(self, path=None, is_remote=False, bucket=None):
        """
        Constructor
        :param path: absolute local path of the file or S3 prefix of the file [String]
        :param is_remote: indicates if the path informed is local or remote (s3 file) [Boolean]
        :param bucket: bucket name [String]
        """
        self._file_path = path
        self._bucket = None
        if path:
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

        else:
            self._file_type = None
            self._file_name = None
            self._file_format = None
            self._file_full_path = None

        try:
            self._session = SparkSession.builder \
                        .master("local") \
                        .appName("sparkApp") \
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

    """
    def to_parquet(self, name=None):
        \"""
        Convert csv file to parquet
        :param name: filename for destination file
        :return: path to the new file
        \"""
        try:
            if not name:
                name = self._file_name
            path = os.path.join(self._file_path, name, '.parquet')

            if self._file_format == 'parquet':
                raise Exception('File loaded is already in parquet format')

            self._dataframe.write.parquet(path)
            return path
        except Exception as ex:
            print(repr(ex))
            raise
    """
