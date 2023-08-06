import logging
import requests
import time

chainsync_defaults = {
    'endpoint': 'http://localhost:8090',
    'endpoints': ['http://localhost:8090'],
}

class BaseAdapter():

    debug = False

    def __init__(self, endpoints=['http://localhost:8090'], retry=True, debug=False):

        self.debug = debug
        # print("debug: {}".format(self.debug))
        self.retry = retry
        # print("retry: {}".format(self.retry))
        self.apis = set()
        # print("apis: {}".format(self.apis))
        self.api_methods = set()
        # print("api_methods: {}".format(self.api_methods))

        # Disable the additional logging unless debug is active
        if not debug:
            request_logger = logging.getLogger('jsonrpcclient.client.request')
            response_logger = logging.getLogger('jsonrpcclient.client.response')
            request_logger.setLevel(logging.getLevelName('WARNING'))
            response_logger.setLevel(logging.getLevelName('WARNING'))

        # Use endpoints or set defaults
        if isinstance(endpoints, list):
            self.endpoint = endpoints[0] if endpoints else chainsync_defaults['endpoint']
            self.endpoints = endpoints if endpoints else chainsync_defaults['endpoints']
        elif isinstance(endpoints, str):
            self.endpoint = endpoints if endpoints else chainsync_defaults['endpoint']
            self.endpoints = [self.endpoint]
        else:
            self.endpoint = chainsync_defaults['endpoint']
            self.endpoints = chainsync_defaults['endpoints']

        # Save a modifiable copy of the endpoints available
        self.additional_endpoints = self.endpoints[:]

        # Remove the active endpoint from the additional_endpoints pool
        if self.endpoint in self.additional_endpoints:
            self.additional_endpoints.remove(self.endpoint)

        # Determine endpoint capabilities
        self.get_available_apis()

    def get_available_apis(self):
        # Get available methods from the current adapter
        available_methods = self.call('get_methods')
        # If available methods is returned as false, assume everything is valid
        if available_methods == 'NOT_SUPPORTED':
            print("get_methods not supported")
        else:
            self.apis = set()
            self.api_methods = set()
            for call in available_methods:
                api, method = call.split('.')
                self.apis.add(api)
                self.api_methods.add(method)

    def is_api_available(self, api, method, raiseException=True):
        if api not in self.apis:
            if raiseException:
                raise Exception('endpoint not capable of calling {}.{} ({} not available)'.format(api, method, api))
            else:
                return False
        return True

    def call(self, method, **kwargs):
        try:
            # Logging
            # print("\n")
            if self.debug:
                print("call: {} ({})".format(method, kwargs))
            # print("endpoint: {}".format(self.endpoint))
            # print("endpoints: {}".format(self.endpoints))
            # print("additional_endpoints: {}".format(self.additional_endpoints))

            # Execute the call against the loaded adapter
            response = getattr(self, method)(**kwargs)

            # TODO - needs better checking
            # if not response:
            #     raise Exception("empty response from API")

            # Return the response
            return response

        except Exception as e:
            # If we have remaining endpoints to try, attempt them
            if len(self.additional_endpoints) > 0:
                # Get the unavailable_endpoint this failed on
                unavailable_endpoint = self.endpoint

                # Get the next additional endpoint and set as the current
                self.endpoint = self.additional_endpoints.pop(0)

                # If we are continiously retrying the servers in the pool
                if self.retry:
                    # Push the previously unavailable back to the end of the list
                    self.additional_endpoints.append(unavailable_endpoint)

                # Determine endpoint capabilities
                self.get_available_apis()

                # Logging
                # print("-------------")
                print("rpcerror: '{}' on {}, swapping to {}...".format(e, unavailable_endpoint, self.endpoint))
                # print("called: {}".format(method))
                # print("kawrgs: {}".format(kwargs))
                # print("-------------")

                time.sleep(0.5)

                # Retry the call with the new endpoint
                return self.call(method, **kwargs)

            # If no endpoints are reachable, and retry enabled, try again
            elif self.retry:
                # print("-------------")
                print("rpcerror: '{}' (retrying in 3 seconds)".format(e))
                # print("endpoint: {}".format(self.endpoint))
                # print("endpoints: {}".format(self.endpoints))
                # print("additional: {}".format(self.additional_endpoints))
                # print("called: {}".format(method))
                # print("kawrgs: {}".format(kwargs))
                # print("-------------")

                time.sleep(3)

                # Try again
                return self.call(method, **kwargs)

            # If no endpoints are reachable, and retry disabled, raise an exception
            else:
                # print("-------------")
                # print("called: {}".format(method))
                # print("kawrgs: {}".format(kwargs))
                # print("-------------")

                raise Exception("rpcerror: '{}' (not retrying)".format(e))
