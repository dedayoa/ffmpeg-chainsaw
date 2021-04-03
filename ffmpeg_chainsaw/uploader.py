import requests
from requests_toolbelt.multipart import encoder
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectTimeout


def http_upload_callback(monitor):
    pass

class UploadTransmitter:

    def __init__(self, file_name, file_mimetype, destination):
        self.file_name = file_name
        self.mimetype = file_mimetype
        self.destination = destination

    def __call__(self, file_handle):
        protocol = self.destination.get('protocol')
        if protocol == "http":
            self.upload_http(file_handle)
        
        file_handle.close()

    def upload_http(self, file):
        configuration = self.destination.get("configuration")
        url = configuration.get("url")
        username = configuration.get("username","")
        password = configuration.get("password","")
        field_name = configuration.get("fieldName", "file")
        
        e = encoder.MultipartEncoder(
            fields={field_name: (self.file_name, file, self.mimetype)}
        )
        m = encoder.MultipartEncoderMonitor(e, http_upload_callback)

        headers = {
            'Content-Type': m.content_type
        }
        try:
            response = None
            if username:
                response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, data=m)
            else:
                response = requests.post(url, data=m, headers=headers)
        except ConnectTimeout:
            pass
        
        print('uploaded http')