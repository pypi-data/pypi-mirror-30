import requests


class ValidationError(Exception):
    pass


class PostCodeClient(object):
    API_ENDPOINT = 'https://api.postcodes.io'
    HTTP_STATUS_SAFE_FOR_PARSING = [requests.codes.ok, requests.codes.not_found]

    def __init__(self):
        self.cache = {}

    def _request(self, method, uri, **values):
        """
        Spawn a request to the API.
        """
        url = self.get_api_endpoint() + uri
        if method == 'GET':
            return requests.get(url, params=values, timeout=5)

    def _get_json(self, postcode, uri):
        """
        Util to parse response or raise generic exception.
        """
        response = self._request('GET', uri)
        if response.status_code in self.get_safe_status():
            # we need response for these two cases.
            return response.json()
        response.raise_for_status()

    def get_api_endpoint(self):
        """
        API endpoint used for retrieving data relevant to a postcode.
        Right now we are using, Postcodes.io.
        @see: https://postcodes.io/

        Override in child class to implement another API.
        Note, you must then override `get` method to point to correct resources.
        """
        return self.API_ENDPOINT

    def get_safe_status(self):
        """
        This method returns the HTTP statuses that are considered
        safe for us to parse JSON from response.

        For example, we need to parse 200 and 404 responses since
        it has relevant information to be shown to user.
        We raise generic exceptions for other cases.
        """
        return self.HTTP_STATUS_SAFE_FOR_PARSING

    def get(self, postcode, skip_cache=False):
        """
        Method that retrieves all information regarding a postcode.
        If the postcode is valid we return a dict containing values explained below,
        {
            "status": 200,
            "result": {
                "postcode": "<formatted postcode>",
                ..
            }
        }
        If postcode is invalid we return a dict containing,
        {
            "status": 404,
            "error": "Invalid postcode."
        }
        For more information, @see: https://postcodes.io/
        """
        if postcode not in self.cache or skip_cache:
            self.cache[postcode] = self._get_json(postcode, '/postcodes/{}/'.format(postcode))
        return self.cache[postcode]

    def clean(self, response):
        """
        Method that cleans the response from API.
        Override in child class to add your validations if neccessary.

        NOTE: On error, must raise `ValidationError`, otherwise, must return the response.
        """
        if response['status'] == requests.codes.not_found:
            # 404 not found. we raise a custom validation error with response from API.
            raise ValidationError(response['error'])
        return response

    def validate(self, postcode, skip_cache=False):
        """
        Method to validate a postcode and return formatted value from API.
        On error, raises `ValidationError`.
        """
        response = self.clean(self.get(postcode, skip_cache))
        return response['result']['postcode']

    def format_code(self, postcode, skip_cache=False):
        """
        Alias for `validate` method.
        This method is here only for explicit call for formatting.
        """
        return self.validate(postcode, skip_cache)
