# -*- coding: utf-8 -*-

"""
    message_media_lookups.models.lookup_a_phone_number_response.
"""


class LookupAPhoneNumberResponse(object):

    """Implementation of the 'Lookup a phone number response' model.

    TODO: type model description here.

    Attributes:
        country_code (string): TODO: type description here.
        phone_number (string): TODO: type description here.
        mtype (string): TODO: type description here.
        carrier (object): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "country_code" : "country_code",
        "phone_number" : "phone_number",
        "mtype" : "type",
        "carrier" : "carrier"
    }

    def __init__(self,
                 country_code=None,
                 phone_number=None,
                 mtype=None,
                 carrier=None):
        """Constructor for the LookupAPhoneNumberResponse class"""

        # Initialize members of the class
        self.country_code = country_code
        self.phone_number = phone_number
        self.mtype = mtype
        self.carrier = carrier


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        country_code = dictionary.get("country_code")
        phone_number = dictionary.get("phone_number")
        mtype = dictionary.get("type")
        carrier = dictionary.get("carrier")

        # Return an object of this model
        return cls(country_code,
                   phone_number,
                   mtype,
                   carrier)
