import pytest
from ffmpeg_chainsaw.uploader import UploadTransmitter, os
import tempfile

class TestUploadTransmitter:

    file_name = 'output.mp3'
    file_mimetype = 'audio/mp3'
    update_callback_data = {}

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
        mock_os_remove = mocker.patch.object(os, 'remove')
        mock_os_remove.side_effect = None
        f = tempfile.NamedTemporaryFile()
        upload_transmitter(f, self.update_callback_data)
        mock_upload.assert_called_with(f)


    def test_upload_http():
        pass
