import logging
import os

import boto3
import pysftp
import requests
from botocore.exceptions import ClientError
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectTimeout
from requests_toolbelt.multipart import encoder

logger = logging.getLogger(__name__)


def http_upload_callback(monitor):
    pass


class UploadTransmitter:
    def __init__(self, file_name, file_mimetype, destination):
        self.file_name = file_name
        self.mimetype = file_mimetype
        self.destination = destination

    def __call__(self, file_handle):
        protocol = self.destination.get('protocol')
        if protocol == "http":
            self.upload_http(file_handle)
        if protocol == "s3":
            self.upload_s3(file_handle)
        if protocol == "sftp":
            self.upload_sftp(file_handle)

        os.remove(file_handle.name)

    def upload_http(self, file):
        configuration = self.destination.get("configuration")
        url = configuration.get("url")
        username = configuration.get("username", "")
        password = configuration.get("password", "")
        field_name = configuration.get("fieldName", "file")

        e = encoder.MultipartEncoder(
            fields={field_name: (self.file_name, file, self.mimetype)})
        m = encoder.MultipartEncoderMonitor(e, http_upload_callback)

        headers = {'Content-Type': m.content_type}
        try:
            response = None
            if username:
                response = requests.post(url,
                                         auth=HTTPBasicAuth(
                                             username, password),
                                         headers=headers,
                                         data=m)
            else:
                response = requests.post(url, data=m, headers=headers)
        except ConnectTimeout:
            pass

        print('uploaded http')

    def upload_s3(self, file):
        configuration = self.destination.get("configuration")
        access_key_id = configuration.get("awsAccessKeyId")
        secret_access_key = configuration.get("awsSecretAccessKey")
        bucket_name = configuration.get("bucketName")
        extra_args = configuration.get("extraArgs", None)

        s3_client = boto3.client('s3',
                                 aws_access_key_id=access_key_id,
                                 aws_secret_access_key=secret_access_key)
        try:
            response = s3_client.upload_fileobj(file,
                                                bucket_name,
                                                self.file_name,
                                                ExtraArgs=extra_args)
        except ClientError as e:
            logger.error(e)
        print('uploaded s3')

    def upload_sftp(self, file):
        configuration = self.destination.get("configuration")
        host = configuration.get("host")
        port = configuration.get("port", 22)
        directory = configuration.get("directory", "")
        username = configuration.get("username")
        password = configuration.get("password")

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        try:
            with pysftp.Connection(host,
                                   port=port,
                                   username=username,
                                   password=password,
                                   cnopts=cnopts) as sftp:
                if directory:
                    sftp.chdir(directory)
                sftp.put(file.name)
        except Exception as e:
            logger.error(e)

        print('uploaded sftp')
