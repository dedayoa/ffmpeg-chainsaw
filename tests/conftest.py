import ffmpeg_chainsaw
import pytest

@pytest.fixture
def app():
    app = ffmpeg_chainsaw.create_app()
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()