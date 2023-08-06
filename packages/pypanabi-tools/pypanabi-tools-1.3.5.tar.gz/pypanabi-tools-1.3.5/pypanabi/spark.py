#!/usr/bin/env python

import os
import logging
from pyspark.sql import *
from .aws import S3


class Spark(object):
    def __init__(self, spark_url='local', appName='PanameraApp', path=None, is_remote=False, bucket=None, profile=None):
        """
        Constructor
        :param spark_url: sets the Spark master URL to connect to, such as 'local' to run locally, or 'spark://master:7077' to run on a Spark standalone cluster
        :param appName = spark application name
        :param path: absolute local path of the file or S3 prefix of the file [String]
        :param is_remote: indicates if the path informed is local or remote (s3 file) [Boolean]
        :param bucket: bucket name [String]
        :param profile: S3 profile [String]
        """
        self._logger = logging.getLogger(__name__)
        self._spark_url = spark_url
        self._appName = appName
        self._dataframe = None
        self._file_path = path
        self._tmp_dir = '/tmp'
        try:
            if path:
                self._file_name = (self._file_path.split(os.sep)[-1]).split('.')[0]
                self._file_format = path.split('.')[-1].lower()
                if is_remote:
                    self._file_source = 's3'
                    self._bucket = bucket

                    if not bucket:
                        raise Exception('S3 bucket must be informed for remote files')

                    if not profile:
                        profile = 'reservoir'

                    # S3 Client
                    self._s3_client = S3(bucket=bucket, profile=profile)

                    if not self._s3_client.exists(self._file_path):
                        raise Exception('File {} does not exist in S3 bucket {}'.format(self._file_path, self._bucket))

                    # Cleaning temporal file if exists
                    tmp_file = os.path.join(self._tmp_dir, self._file_name + '.' + self._file_format)
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)

                else:
                    self._file_source = 'file'
                    self._bucket = ''

                self._full_file_path = self._file_source + '://' + os.path.join(self._bucket, self._file_path)

                # Spark session
                self._session = SparkSession.builder \
                    .master(self._spark_url) \
                    .appName(self._appName) \
                    .enableHiveSupport() \
                    .getOrCreate()

            else:
                self._bucket = None
                self._session = None
                self._file_type = None
                self._file_name = None
                self._file_format = None
                self._full_file_path = None

        except Exception as ex:
            self._logger.error(repr(ex))

    def set_file(self, path, is_remote=False, bucket=None, profile=None):
        """
        Set file path (remote or local file)
        :param path: absolute local path of the file or S3 prefix of the file [String]
        :param is_remote: indicates if the path informed is local or remote (s3 file) [Boolean]
        :param bucket: bucket name [String]
        :param profile: S3 profile [String]
        :return: None
        """
        self._file_path = path
        self._file_name = (self._file_path.split(os.sep)[-1]).split('.')[0]
        self._file_format = path.split('.')[-1].lower()
        if is_remote:
            self._file_source = 's3'
            self._bucket = bucket

            if not bucket:
                raise Exception('S3 bucket must be informed for remote files')

            if not profile:
                profile = 'reservoir'

            # S3 Client
            self._s3_client = S3(bucket=bucket, profile=profile)

            if not self._s3_client.exists(self._file_path):
                raise Exception('File {} does not exist in S3 bucket {}'.format(self._file_path, self._bucket))

            # Cleaning temporal file if exists
            tmp_file = os.path.join(self._tmp_dir, self._file_name + '.' + self._file_format)
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        else:
            self._file_source = 'file'
            self._bucket = ''

        self._full_file_path = self._file_source + '://' + os.path.join(self._bucket, self._file_path)

        # Spark session
        if not self._session:
            self._session = SparkSession.builder \
                .master(self._spark_url) \
                .appName(self._appName) \
                .enableHiveSupport() \
                .getOrCreate()

    def read(self):
        """
        Read file local or remote
        :return: dataframe with data loaded from file [Dataframe]
        """
        if not self._full_file_path:
            raise Exception('No file informed. Use set_file method for this purpose and run it again')

        try:
            if self._file_source == 's3':
                tmp_file = os.path.join(self._tmp_dir, self._file_name + '.' + self._file_format)

                # Remove tmp file if exists
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)

                local_path = self._s3_client.download(prefix=self._file_path, local_path=self._tmp_dir)[0]
            else:
                local_path = self._full_file_path

            # Reading file and saving it in memory
            self._dataframe = self._session.read.load(local_path, format=self._file_format)
            #SQLContext.cacheTable(self._dataframe)

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_dataframe(self):
        """
        Get dataframe
        :return: data [Dataframe]
        """
        return self._dataframe

    def get_columns(self):
        """
        Get dataframe columns
        :return: list with all columns [List]
        """
        if self._dataframe:
            return self._dataframe.columns

    def remove_columns(self, columns):
        """
        Remove columns from dataframe
        :param columns: list of columns [List<String>]
        :return: None
        """
        for col in columns:
            try:
                self._dataframe = self._dataframe.drop(col)
            except Exception as ex:
                self._logger.warning(repr(ex))
                pass

    def get_partition_value(self, partition):
        """
        Get value for an specified partition
        :param partition: partition name [String]
        :return: value for partition or None if partition does not exist
        """
        value = None
        if self._file_path:
            for pair in (x for x in self._file_path.split(os.sep) if '=' in x):
                val = pair.split('=')
                if val[0] == partition:
                    value = val[1]
                    break
        return value

    def rename_columns(self, columns):
        """
        Rename columns
        :param columns: dictionary with old name as key and new name as value [Dictionary]
        :return: None
        """
        for key, value in columns.iteritems:
            try:
                self._dataframe = self._dataframe.withColumnRenamed(key, value)
            except Exception as ex:
                self._logger.warning(repr(ex))
                pass

    def save_to_cassandra(self, keyspace, table, mode='overwrite'):
        """
        Save dataframe to Cassandra
        :param keyspace: keyspace name [String]
        :param table: table name in Cassandra [String]
        :param mode: writing mode append, overwrite, ignore, error [String]
        :return: None
        """
        try:
            if self._dataframe:
                self._dataframe.write \
                    .format("org.apache.spark.sql.cassandra") \
                    .mode(mode) \
                    .options(keyspace=keyspace, table=table) \
                    .save()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def __repr__(self):
        return str({'AppName': self._appName, 'MasterURL': self._spark_url, 'File Path': self._full_file_path})