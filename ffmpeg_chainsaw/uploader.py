import logging
import os
import shutil

import boto3
import pysftp
import requests
from botocore.exceptions import ClientError
from requests.auth import HTTPBasicAuth
from requests_toolbelt.multipart import encoder
from .helpers import send_update

logger = logging.getLogger(__name__)


def http_upload_callback(monitor):
    pass


class UploadTransmitter:
    """Responsible for uploding(or copying) processed file

    Args:
        file_name (str): the name of the processed file
        file_mimetype (str): the mime type of the processed file
        destination (dict): dictionary that described the upload (or copy) destination
    """
    def __init__(self, file_name, file_mimetype, destination):
        self.file_name = file_name
        self.mimetype = file_mimetype
        self.destination = destination

    def __call__(self, file_handle, update_callback_data):
        protocol = self.destination.get('protocol')
        self.update_callback_data = update_callback_data
        if protocol == "http":
            self.upload_http(file_handle)
        if protocol == "s3":
            self.upload_s3(file_handle)
        if protocol == "sftp":
            self.upload_sftp(file_handle)
        if protocol == "disk":
            self.copy_disk(file_handle)

        os.remove(file_handle.name)            

    def _upload_processed_file(self, url, data, headers: dict, username="", password=""):
        if "Content-Type" not in headers.keys():
            raise KeyError("'Content-Type' header is required")
        
        try:
            response = None
            if username:
                response = requests.post(url,
                                         auth=HTTPBasicAuth(
                                             username, password),
                                         headers=headers,
                                         data=data)
            else:
                response = requests.post(url, data=data, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"request returned status code {response.status_code}")
            
            send_update('INFO', 'file uploaded successfully with http', self.update_callback_data)
        except Exception as e:
            logger.error(e)
            send_update('ERROR', f'http file upload failed. {e}', self.update_callback_data)

    def upload_http(self, file):
        configuration = self.destination.get("configuration")
        url = configuration.get("url")
        username = configuration.get("username", "")
        password = configuration.get("password", "")
        field_name = configuration.get("fieldName", "file")
        custom_headers = configuration.get("customHeaders", {})

        e = encoder.MultipartEncoder(
            fields={field_name: (self.file_name, file, self.mimetype)})
        m = encoder.MultipartEncoderMonitor(e, http_upload_callback)

        headers = {'Content-Type': m.content_type} | custom_headers

        self._upload_processed_file(url, m, headers, username, password)

        

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
            s3_client.upload_fileobj(file,
                                    bucket_name,
                                    self.file_name,
                                    ExtraArgs=extra_args)
            send_update('INFO', 'file uploaded successfully with s3', self.update_callback_data)
        except ClientError as e:
            logger.error(e)
            send_update('ERROR', f's3 file upload failed. {e}', self.update_callback_data)

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
            send_update('INFO', 'file uploaded successfully with sftp', self.update_callback_data)
        except Exception as e:
            logger.error(e)
            send_update('ERROR', f'sftp file upload failed. {e}', self.update_callback_data)

    def copy_disk(self, file):
        configuration = self.destination.get("configuration")
        directory = configuration.get("directory")

        if not os.path.isdir(directory):
            return

        try:
            shutil.copyfile(
                file.name, os.path.join(directory,
                                        os.path.basename(file.name)))
            send_update('INFO', 'file copied successfully', self.update_callback_data)
        except Exception as e:
            logger.error(e)
            send_update('ERROR', f'disk file copy failed. {e}', self.update_callback_data)
