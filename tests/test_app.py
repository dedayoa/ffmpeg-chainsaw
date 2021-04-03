from flask.helpers import url_for
import pytest
from ffmpeg_chainsaw.app import request
import io
import json

def test_hello(client):
    assert client.get(url_for('app.hello')).status_code == 200

def test_e400_upload_to_process_if_no_file(client):
    assert client.post(url_for('app.upload_to_process')).status_code == 400

def test_upload_to_process(client):
    response = client.post(url_for('app.upload_to_process'),
        data={
            "file": (io.BytesIO(b"MyAudioFile"), "testfile.mp3"),
            "instruction": json.dumps({"price": "hi"})
        },
        content_type="multipart/form-data"
    )
    assert response.status_code == 200