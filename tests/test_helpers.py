from ffmpeg_chainsaw.helpers import (logger, requests, send_update,
                                     thread_it, threading)
from requests.models import HTTPBasicAuth


def test_thread_it(mocker):
    func = mocker.Mock()
    mock_thread = mocker.patch.object(threading, 'Thread', autospec=True)
    wrapped_func = thread_it(func)
    wrapped_func().join()

    mock_thread.assert_called_with(target=func, args=(), kwargs={})
    assert wrapped_func().daemon == True
    wrapped_func().start.assert_called()



class TestSendUpdate:

    category = 'INFO'
    message = 'Hello'
    url = "https://webhook.site/60fd317f-3ea3-4412-aa90-99b951efa677"
    custom_headers = {}
    password = 'pass'

    def test_send_update_none_update_service_data(self, mocker):
        mock_logger = mocker.patch.object(logger, 'warning', autospec=True)
        update_service_data = {}
        result = send_update(self.category, self.message, update_service_data)

        mock_logger.assert_called_once_with(
            "updateCallback in instruction is not configured properly. Request not sent to update webhook"
        )
        assert result == None

    def test_send_update_with_username(self, mocker, mocked_datetime_now):
        mock_request = mocker.patch.object(requests, 'post', autospec=True)
        data = {
            "time": mocked_datetime_now,
            "category": self.category,
            "message": self.message
        }

        username = "dayo"
        update_service_data = {
            "url": self.url,
            "username": username,
            "password": self.password
        }

        send_update(self.category, self.message, update_service_data)
        mock_request.assert_called_with(self.url,
                                        data=data,
                                        headers=self.custom_headers,
                                        auth=HTTPBasicAuth(
                                            username, self.password))

    def test_send_update_without_username(self, mocker, mocked_datetime_now):
        mock_request = mocker.patch.object(requests, 'post', autospec=True)
        data = {
            "time": mocked_datetime_now,
            "category": self.category,
            "message": self.message
        }

        username = ""
        update_service_data = {
            "url": self.url,
            "username": username,
            "password": self.password
        }

        send_update(self.category, self.message, update_service_data)
        mock_request.assert_called_with(self.url,
                                        data=data,
                                        headers=self.custom_headers)
