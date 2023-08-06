# -*- coding: utf-8 -*-

"""
    tests.controllers.test_lookups_controller.
"""

import jsonpickle
import dateutil.parser
from .controller_test_base import ControllerTestBase
from ..test_helper import TestHelper
from message_media_lookups.api_helper import APIHelper


class LookupsControllerTests(ControllerTestBase):

    @classmethod
    def setUpClass(cls):
        super(LookupsControllerTests, cls).setUpClass()
        cls.controller = cls.api_client.lookups

    # Use the Lookups API to find information about a phone number.
    #A request to the lookups API has the following format:
    #```/v1/lookups/phone/{phone_number}?options={carrier,type}```
    #The `{phone_number}` parameter is a required field and should be set to the phone number to be looked up.
    #The options query parameter can also be used to request additional information about the phone number.
    #By default, a request will only return the `country_code` and `phone_number` properties in the response.
    #To request details about the the carrier, include `carrier` as a value of the options parameter.
    #To request details about the type, include `type` as a value of the options parameter. To pass multiple values
    #to the options parameter, use a comma separated list, i.e. `carrier,type`.
    #A successful request to the lookups endpoint will return a response body as follows:
    #```json
    #{
    #  "country_code": "AU",
    #  "phone_number": "+61491570156",
    #  "type": "mobile",
    #  "carrier": {
    #    "name": "Telstra"
    #  }
    #}
    #```
    #Each property in the response body is defined as follows:
    #- ```country_code``` ISO ALPHA 2 country code of the phone number
    #- ```phone_number``` E.164 formatted phone number
    #- ```type``` The type of number. This can be ```"mobile"``` or ```"landline"```
    #- ```carrier``` Holds information about the specific carrier (if available)
    #  - ```name``` The carrier's name as reported by the network
    def test_lookup_a_phone_number(self):
        # Parameters for the API call
        phone_number = '+61491570156'
        options = 'carrier,type'

        # Perform the API call through the SDK function
        result = self.controller.get_lookup_a_phone_number(phone_number, options)

        # Test response code
        self.assertEquals(self.response_catcher.response.status_code, 200)

        # Test headers
        expected_headers = {}
        expected_headers['content-type'] = None

        self.assertTrue(TestHelper.match_headers(expected_headers, self.response_catcher.response.headers))


        # Test whether the captured response is as we expected
        self.assertIsNotNone(result)
        self.assertEqual('{"countryCode":"AU","phoneNumber":"+61491570156","type":"MOBILE","carrier":{"name":"AU Landline Carrier"}}', self.response_catcher.response.raw_body)
