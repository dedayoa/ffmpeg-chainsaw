import functools
import threading
import logging
import requests
import datetime

from requests.models import HTTPBasicAuth

logger = logging.getLogger(__name__)


def thread_it(func):
    """A wrapper function to run func in a daemon thread.

    Args:
        func (function): The function to run in a thread

    Returns:
        function: the wrapped function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread #returning to support unit testing

    return wrapper


def send_update(category, message, update_service_data):
    """Sends message (application updates) to an http endpoint
    """
    if not update_service_data:
        logger.warning(
            "updateCallback in instruction is not configured properly. Request not sent to update webhook"
        )
        return

    data = {"time": datetime.datetime.now(), "category": category, "message": message}
    url = update_service_data.get('url', "")
    custom_headers = update_service_data.get('customHeaders', {})
    username = update_service_data.get('username', "")
    password = update_service_data.get('password', "")

    try:
        if username:
            requests.post(url,
                          data=data,
                          headers=custom_headers,
                          auth=HTTPBasicAuth(username, password))
        else:
            requests.post(url, data=data, headers=custom_headers)
    except Exception as e:
        logger.error(e)