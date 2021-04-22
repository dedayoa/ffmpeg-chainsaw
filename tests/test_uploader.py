import pytest
from ffmpeg_chainsaw.uploader import UploadTransmitter, boto3, \
    requests, HTTPBasicAuth, encoder, http_upload_callback, os
import tempfile

class TestUploadTransmitter:

    update_callback_data = {}
    file_name = 'output.mp3'
    file_mimetype = 'audio/mp3'

    @pytest.mark.parametrize(
        "protocol, method_name", [
            ("s3", "upload_s3"),
            ("http", "upload_http"),
            ("sftp", "upload_sftp"),
            ("disk", "copy_disk")]
    )
    def test__call__(self, mocker, protocol, method_name):
        destination = {"protocol": protocol, "configuration": {}}

        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        mock_upload = mocker.patch.object(UploadTransmitter, method_name)
        mock_upload.side_effect = None
        f = tempfile.NamedTemporaryFile(delete=False)
        upload_transmitter(f, self.update_callback_data)
        mock_upload.assert_called_with(f)

    def test_upload_http(self, mocker, http_upload_configuration):
        
        upload_destination_configuration = http_upload_configuration["configuration"]
        url = upload_destination_configuration["url"]
        custom_headers = upload_destination_configuration["customHeaders"]
        username = upload_destination_configuration["username"]
        
        f = tempfile.NamedTemporaryFile(delete=False)
        
        e = encoder.MultipartEncoder(
            fields={"grubby": (self.file_name, f, self.file_mimetype)}
            )
        mock_multipartencoder = mocker.patch.object(encoder, 'MultipartEncoder', autospec=True)
        mock_multipartencoder.return_value = e

        m = encoder.MultipartEncoderMonitor(e, http_upload_callback)
        mock_multipartencodermonitor = mocker.patch.object(encoder, 'MultipartEncoderMonitor', autospec=True)
        mock_multipartencodermonitor.return_value = m

        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, http_upload_configuration)
        mock___upload_processed_file = mocker.patch.object(upload_transmitter, '_upload_processed_file')
        
        upload_transmitter.upload_http(f)
        
        mock___upload_processed_file.assert_called_with(
            url,
            m,
            {"Content-Type": m.content_type} | custom_headers,
            username,
            ""
        )

    def test__upload_processed_file_raise_keyerror_when_no_content_type(self, mocker):
        destination = {"protocol": "http", "configuration": {}}
        url = 'http://url.com'
        headers = {"Age": 10}
        mock_data = mocker.patch('ffmpeg_chainsaw.uploader.encoder.MultipartEncoderMonitor')

        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        
        with pytest.raises(KeyError):
            upload_transmitter._upload_processed_file(url, mock_data, headers)

    
    def test__upload_processed_file(self, mocker):
        url = 'http://url.com'
        headers = {"Content-Type": "audio/wav", "Age": 10}
        update_callback_data = {"url": "http://updatedest.net/update.cgi"}
        username = "user1"
        destination = {"protocol": "http", "configuration": {}}
        mock_data = mocker.patch('ffmpeg_chainsaw.uploader.encoder.MultipartEncoderMonitor')
        mock_send_update = mocker.patch('ffmpeg_chainsaw.uploader.send_update')

        mock_post_request = mocker.patch.object(requests, 'post', autospec=True)
        mock_post_request.return_value.status_code = 200

        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        upload_transmitter.update_callback_data = update_callback_data
        upload_transmitter._upload_processed_file(url, mock_data, headers, username)
        
        mock_post_request.assert_called_with(
            url,
            auth=HTTPBasicAuth(username, ""),
            headers = headers,
            data=mock_data
        )
        mock_send_update.assert_called_with('INFO', 'file uploaded successfully with http', update_callback_data)

    def test__upload_processed_file_raises_exception_when_response_status_code_not_200(self, mocker):
        url = 'http://url.com'
        headers = {"Content-Type": "audio/wav", "Age": 10}
        update_callback_data = {"url": "http://updatedest.net/update.cgi"}
        username = "user1"
        destination = {"protocol": "http", "configuration": {}}
        mock_data = mocker.patch('ffmpeg_chainsaw.uploader.encoder.MultipartEncoderMonitor')
        mock_send_update = mocker.patch('ffmpeg_chainsaw.uploader.send_update')

        mock_post_request = mocker.patch.object(requests, 'post', autospec=True)
        mock_post_request.return_value.status_code = 404

        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        upload_transmitter.update_callback_data = update_callback_data
        
        with pytest.raises(Exception) as e:
            upload_transmitter._upload_processed_file(url, mock_data, headers, username)
            
            mock_send_update.assert_called_with('ERROR', f'http file upload failed. {e}', update_callback_data)

    def test__upload_processed_file_when_no_auth(self, mocker):
        url = 'http://url.com'
        headers = {"Content-Type": "audio/wav", "Age": 10}
        update_callback_data = {"url": "http://updatedest.net/update.cgi"}
        destination = {"protocol": "http", "configuration": {}}
        mock_data = mocker.patch('ffmpeg_chainsaw.uploader.encoder.MultipartEncoderMonitor')
        mock_send_update = mocker.patch('ffmpeg_chainsaw.uploader.send_update')

        mock_post_request = mocker.patch.object(requests, 'post', autospec=True)
        mock_post_request.return_value.status_code = 200

        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        upload_transmitter.update_callback_data = update_callback_data
        upload_transmitter._upload_processed_file(url, mock_data, headers)
        
        mock_post_request.assert_called_with(
            url,
            headers = headers,
            data=mock_data
        )
            
        mock_send_update.assert_called_with('INFO', 'file uploaded successfully with http', update_callback_data)

    def test_upload_s3(self, mocker):
        access_key_id = "accessKeyId"
        secret_access_key = "secretAccessKey"
        bucket_name = "bucketName"
        extra_args = None
        update_callback_data = {"url": "http://updatedest.net/update.cgi"}
        destination = {"protocol": "http", "configuration": {
            "awsAccessKeyId": access_key_id,
            "awsSecretAccessKey": secret_access_key,
            "bucketName": bucket_name,
        }}
        f = tempfile.NamedTemporaryFile(delete=False)
        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        upload_transmitter.update_callback_data = update_callback_data
        
        mock_boto3_client = mocker.patch('ffmpeg_chainsaw.uploader.boto3.client')
        mock_send_update = mocker.patch('ffmpeg_chainsaw.uploader.send_update')
        
        upload_transmitter.upload_s3(f)
        
        mock_boto3_client.assert_called_with(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
        mock_send_update.assert_called_with('INFO', 'file uploaded successfully with s3', update_callback_data)

    def test_upload_sftp(self, mocker):
        update_callback_data = {"url": "http://updatedest.net/update.cgi"}
        host = "1.1.1.1"
        port = "2222"
        directory = "/store"
        username = "user1"
        password = "pass"
        destination = {"protocol": "sftp", "configuration": {
            "host": host,
            "port": port,
            "directory": directory,
            "username": username,
            "password": password
        }}
        f = tempfile.NamedTemporaryFile(delete=False)
        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        upload_transmitter.update_callback_data = update_callback_data
        mock_send_update = mocker.patch('ffmpeg_chainsaw.uploader.send_update')

        mock_sftp_connection_options = mocker.patch('ffmpeg_chainsaw.uploader.pysftp.CnOpts')
        mock_sftp_connection_options.host_keys.return_value = None

        mock_sftp_connection = mocker.patch('ffmpeg_chainsaw.uploader.pysftp.Connection')

        upload_transmitter.upload_sftp(f)

        mock_sftp_connection.assert_called_with(
            host,
            port=port,
            username=username,
            password=password,
            cnopts=mock_sftp_connection_options()
        )
        mock_send_update.assert_called_with('INFO', 'file uploaded successfully with sftp' , update_callback_data)


    def test_copy_disk(self, mocker):
        directory = "/tmp/final"
        destination = {"protocol": "disk", "configuration": {
            "directory": directory
        }}
        update_callback_data = {"url": "http://updatedest.net/update.cgi"}
        
        f = tempfile.NamedTemporaryFile(delete=False)
        upload_transmitter = UploadTransmitter(self.file_name, self.file_mimetype, destination)
        upload_transmitter.update_callback_data = update_callback_data
        mock_send_update = mocker.patch('ffmpeg_chainsaw.uploader.send_update')
        
        mock_isdir = mocker.patch('ffmpeg_chainsaw.uploader.os.path.isdir')
        mock_isdir.return_value = True

        mock_copy = mocker.patch('ffmpeg_chainsaw.uploader.shutil.copyfile')

        upload_transmitter.copy_disk(f)

        basename = os.path.basename(f.name)
        dest_path = os.path.join(directory, basename)

        mock_copy.assert_called_with(
            f.name, dest_path
        )
        mock_send_update.assert_called_with('INFO', 'file written to disk successfully', update_callback_data)
