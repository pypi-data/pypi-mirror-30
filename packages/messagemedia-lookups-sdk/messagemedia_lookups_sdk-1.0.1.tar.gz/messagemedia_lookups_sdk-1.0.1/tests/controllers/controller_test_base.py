# -*- coding: utf-8 -*-

"""
    tests.controllers.controller_test_base.
"""

import unittest
from ..http_response_catcher import HttpResponseCatcher
from message_media_lookups.message_media_lookups_client import MessageMediaLookupsClient
from message_media_lookups.configuration import Configuration

class ControllerTestBase(unittest.TestCase):

    """All test classes inherit from this base class. It abstracts out
    common functionality and configuration variables set up."""

    @classmethod
    def setUpClass(cls):
        """Class method called once before running tests in a test class."""
        cls.api_client = MessageMediaLookupsClient()
        cls.request_timeout = 30
        cls.assert_precision = 0.01

        Configuration.basic_auth_user_name = os.environ['MessageMediaApiTestsKey']
        Configuration.basic_auth_password = os.environ['MessageMediaApiTestsSecret']

    def setUp(self):
        """Method called once before every test in a test class."""
        self.response_catcher = HttpResponseCatcher()
        self.controller.http_call_back =  self.response_catcher
