import io
import json

import pytest
from ffmpeg_chainsaw.app import psutil
from flask.helpers import url_for
from jsonschema.exceptions import ValidationError


def test_hello(client):
    assert client.get(url_for('app.hello')).status_code == 200


def test_e400_upload_to_process_if_no_file(client):
    response = client.post(url_for('app.upload_to_process'))
    assert response.status_code == 400


def test_e400_upload_to_process_missing_instruction(client):
    response = client.post(url_for('app.upload_to_process'),
                           data={
                               "file":
                               (io.BytesIO(b"MyAudioFile"), "testfile.mp3"),
                           },
                           content_type="multipart/form-data")
    assert response.status_code == 400


def test_e400_upload_to_process_failed_instruction_validation(client, mocker):
    mock_validate = mocker.patch('ffmpeg_chainsaw.app.validate')
    mock_validate.side_effect = ValidationError('validation failed')
    response = client.post(url_for('app.upload_to_process'))
    assert response.status_code == 400


@pytest.mark.parametrize(
    "cpu_percent, status_code", [
        (2, 200),
        (95, 200),
        (96, 503),
        (100, 503)
    ])
def test_upload_to_process(client, mocker, cpu_percent, status_code):
    mock_validate = mocker.patch('ffmpeg_chainsaw.app.validate')
    mock_validate.side_effect = None
    mock_process_file = mocker.patch('ffmpeg_chainsaw.app.process_file')
    mock_process_file.side_effect = None
    mock_psutil_cpu_percent = mocker.patch.object(psutil,
                                                  'cpu_percent',
                                                  autospec=True)
    mock_psutil_cpu_percent.return_value = cpu_percent
    response = client.post(url_for('app.upload_to_process'),
                           data={
                               "file":
                               (io.BytesIO(b"MyAudioFile"), "testfile.mp3"),
                               "instruction": json.dumps({"price": "hi"})
                           },
                           content_type="multipart/form-data")
    assert response.status_code == status_code
