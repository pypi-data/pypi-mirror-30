# -*- coding: utf-8 -*-

"""
    message_media_lookups.message_media_lookups_client.
"""
from .decorators import lazy_property
from .configuration import Configuration
from .controllers.lookups_controller import LookupsController

class MessageMediaLookupsClient(object):

    config = Configuration

    @lazy_property
    def lookups(self):
        return LookupsController()


    def __init__(self,
                 basic_auth_user_name = None,
                 basic_auth_password = None):
        if basic_auth_user_name != None:
            Configuration.basic_auth_user_name = basic_auth_user_name
        if basic_auth_password != None:
            Configuration.basic_auth_password = basic_auth_password
