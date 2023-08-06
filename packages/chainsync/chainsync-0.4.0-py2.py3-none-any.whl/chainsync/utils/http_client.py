import requests
import sys
import datetime
import time

from jsonrpcclient import config
from jsonrpcclient.exceptions import ParseResponseError
from jsonrpcclient.http_client import HTTPClient
from jsonrpcclient.prepared_request import PreparedRequest
from jsonrpcclient.request import Request
config.validate = False

class HttpClient(HTTPClient):

    def send(self, request, **kwargs):
        # start_time = time.time()
        response = super(HttpClient, self).send(request, **kwargs)
        # total_time = "%.3f" % (time.time() - start_time)
        # print("[{}] http request - {} kb / {} sec - {} {}".format(datetime.datetime.now(), sys.getsizeof(str(response)) / 1000, total_time, request, list(kwargs)))
        # print(response)
        if 'error' in response:
            print("response error")
            print(response)
            raise requests.RequestException()
        return response

    def request(self, method_name, *args, **kwargs):
        # start_time = time.time()
        response = super(HttpClient, self).send(Request(method_name, *args, **kwargs))
        # total_time = "%.3f" % (time.time() - start_time)
        # print("[{}] http request - {} kb / {} sec - {} {}".format(datetime.datetime.now(), sys.getsizeof(str(response)) / 1000, total_time, method_name, list(args)))
        # print(response)
        if 'error' in response:
            print("response error")
            print(response)
            raise requests.RequestException()
        return response
