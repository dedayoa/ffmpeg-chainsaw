import ffmpeg_chainsaw
import pytest
import datetime
import tempfile

@pytest.fixture
def app():
    app = ffmpeg_chainsaw.create_app()
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def mocked_datetime_now(mocker):
    now = datetime.datetime.now()    
    mock_datetime = mocker.patch('ffmpeg_chainsaw.helpers.datetime')
    mock_datetime.datetime.now.return_value = now
    yield now

@pytest.fixture
def http_upload_configuration():
    return {
        "protocol": "http",
        "configuration": {
            "username": "provided",
            "url": "http://destination.com/upload.cgi",
            "fieldName": "grubby",
            "customHeaders": {
                "Age": 30
            }
        }
    }

