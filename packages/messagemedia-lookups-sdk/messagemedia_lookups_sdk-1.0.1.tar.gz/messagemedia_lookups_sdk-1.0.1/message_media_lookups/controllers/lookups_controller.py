# -*- coding: utf-8 -*-

"""
    message_media_lookups.controllers.lookups_controller.
"""

import logging
from .base_controller import BaseController
from ..api_helper import APIHelper
from ..configuration import Configuration
from ..http.auth.basic_auth import BasicAuth
from ..models.lookup_a_phone_number_response import LookupAPhoneNumberResponse
from ..exceptions.api_exception import APIException

class LookupsController(BaseController):

    """A Controller to access Endpoints in the message_media_lookups API."""

    def __init__(self, client=None, call_back=None):
        super(LookupsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)

    def get_lookup_a_phone_number(self,
                                  phone_number,
                                  options=None):
        """Does a GET request to /v1/lookups/phone/{phone_number}.

        Use the Lookups API to find information about a phone number.
        A request to the lookups API has the following format:
        ```/v1/lookups/phone/{phone_number}?options={carrier,type}```
        The `{phone_number}` parameter is a required field and should be set
        to the phone number to be looked up.
        The options query parameter can also be used to request additional
        information about the phone number.
        By default, a request will only return the `country_code` and
        `phone_number` properties in the response.
        To request details about the the carrier, include `carrier` as a value
        of the options parameter.
        To request details about the type, include `type` as a value of the
        options parameter. To pass multiple values
        to the options parameter, use a comma separated list, i.e.
        `carrier,type`.
        A successful request to the lookups endpoint will return a response
        body as follows:
        ```json
        {
          "country_code": "AU",
          "phone_number": "+61491570156",
          "type": "mobile",
          "carrier": {
            "name": "Telstra"
          }
        }
        ```
        Each property in the response body is defined as follows:
        - ```country_code``` ISO ALPHA 2 country code of the phone number
        - ```phone_number``` E.164 formatted phone number
        - ```type``` The type of number. This can be ```"mobile"``` or
        ```"landline"```
        - ```carrier``` Holds information about the specific carrier (if
        available)
          - ```name``` The carrier's name as reported by the network

        Args:
            phone_number (string): The phone number to be looked up
            options (string, optional): TODO: type description here. Example:

        Returns:
            LookupAPhoneNumberResponse: Response from the API.

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_lookup_a_phone_number called.')

            # Prepare query URL
            self.logger.info('Preparing query URL for get_lookup_a_phone_number.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/lookups/phone/{phone_number}'
            _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, {
                'phone_number': phone_number
            })
            _query_parameters = {
                'options': options
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, Configuration.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_lookup_a_phone_number.')
            _headers = {
                'accept': 'application/json',
                'user-agent': 'messagemedia-lookups-python-sdk-1.0.0'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_lookup_a_phone_number.')
            _request = self.http_client.get(_query_url, headers=_headers)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'get_lookup_a_phone_number')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_lookup_a_phone_number.')
            if _context.response.status_code == 404:
                raise APIException('Number was invalid', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, LookupAPhoneNumberResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
