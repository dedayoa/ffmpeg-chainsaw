import io
import json
import uuid

import pytest
from ffmpeg_chainsaw.app import psutil, current_app, UploadTransmitter
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
def test_upload_to_process_cpu_percent(client, mocker, cpu_percent, status_code):
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


def test_upload_to_process(client, mocker):
    mock_validate = mocker.patch('ffmpeg_chainsaw.app.validate')
    mock_validate.side_effect = None

    mock_process_file = mocker.patch('ffmpeg_chainsaw.app.process_file')    
    
    file_name = str(uuid.uuid4())
    mock_file_name = mocker.patch('ffmpeg_chainsaw.app.uuid.uuid4')
    mock_file_name.return_value = file_name
    file_loc = current_app.config.get('BASE_DIR').joinpath(
        'incoming', file_name)
    
    file_mimetype = "audio/wav"
    destination = {"protocol": "disk", "configuration": {}}

    output_file_ext = "wav"
    output_file_name = f"{file_name}.{output_file_ext}"
    upload_transmitter = UploadTransmitter(output_file_name, file_mimetype, destination)
    mock_upload_transmitter = mocker.patch('ffmpeg_chainsaw.app.UploadTransmitter')
    mock_upload_transmitter.return_value = upload_transmitter

    ffmpeg_arguments = ["-codec", "copy"]
    update_callback_data = {"url": "http://updatedest.net/update.cgi"}
    response = client.post(url_for('app.upload_to_process'),
                           data={
                               "file":
                               (io.BytesIO(b"MyAudioFile"), "testfile.mp3"),
                               "instruction": json.dumps({
                                   "ffmpegArgs": ffmpeg_arguments,
                                   "outputFileExt": output_file_ext,
                                   "destination": destination,
                                   "updateCallback": update_callback_data
                                })
                            },
                            content_type="multipart/form-data")
    mock_process_file.assert_called_with(
        file_loc, ffmpeg_arguments, upload_transmitter, update_callback_data
    )
    assert response.status_code == 200