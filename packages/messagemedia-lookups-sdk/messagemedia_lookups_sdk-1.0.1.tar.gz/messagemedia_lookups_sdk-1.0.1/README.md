# MessageMedia Lookups Python SDK
[![Build Status](https://travis-ci.org/messagemedia/lookups-python-sdk.svg?branch=master)](https://travis-ci.org/messagemedia/lookups-python-sdk)
[![PyPI](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.python.org/pypi/messagemedia-lookups-sdk)

The MessageMedia Lookups API provides a number of endpoints for validating the phone numbers you’re sending to by checking their validity, type and carrier records.

## ⭐️ Installing via pip
Run the following command to install the SDK via pip: `pip install messagemedia-lookups-sdk`

## 🎬 Get Started
It's easy to get started. Simply enter the API Key and secret you obtained from the [MessageMedia Developers Portal](https://developers.messagemedia.com) into the code snippet below and a mobile number you wish to send to.

### 👀 Lookup a number
```python
# Configuration parameters and credentials
from message_media_lookups.message_media_lookups_client import MessageMediaLookupsClient
import json

basic_auth_user_name = 'YOUR_API_KEY' # The username to use with basic authentication
basic_auth_password = 'YOUR_API_SECRET' # The password to use with basic authentication

client = MessageMediaLookupsClient(basic_auth_user_name, basic_auth_password)

lookups_controller = client.lookups

phone_number = 'YOUR_MOBILE_NUMBER'
options = 'carrier,type'

result = lookups_controller.get_lookup_a_phone_number(phone_number, options)
```

## 📕 Documentation
The Python SDK Documentation can be viewed [here](DOCUMENTATION.md)

## 😕 Need help?
Please contact developer support at developers@messagemedia.com or check out the developer portal at [developers.messagemedia.com](https://developers.messagemedia.com/)
