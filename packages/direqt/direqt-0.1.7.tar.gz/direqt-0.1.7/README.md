# Direqt Software Development Kit for Python

Direqt is an advertising platform for chatbots.

The Direqt Software Development Kit (SDK) for Python contains library code and examples designed to enable developers to
integrate ads into chatbot agents written in Python. This SDK current supports only RCS agents using Google's RBM APIs.

    $ pip install direqt    # install library locally (or into a virtualenv)
    
Before using the SDK, you need an API key from <https://www.direqt.io>. You will also need to have configured one or
more ad units for your agent's network in order to dynamically fetch ads.

### Quick Peek:

```python
from direqt import DireqtClient
API_KEY = "<API_KEY>" # from management console

direqt = DireqtClient(API_KEY)    # create SDK instance

def deliver_ad(msisdn, ad_unit): 
    """Fetch an ad for the specified ad_unit, and deliver it to the user."""
    direqt.fetch(ad_unit=ad_unit, msisdn=msisdn)
```

### Supported Messaging Platforms

Direqt can be used with both SMS and RCS messaging platforms.

For RCS, we support Google RBM APIs natively. If you are using RBM, the SDK can 
automatically recognize ad units, fetch ads from the server, and handle the sending
and receiving of related user messages without requiring any changes to your agent
logic.

For SMS, the SDK handles the fetching of targeted ads for users at your defined 
conversation moments, and returns them to your agent as ready-to-send payloads.
Your application is then responsible for actually delivering the payload to the
user using your choice of messaging platform.

The default platform is RBM. To use SMS, specify `ad_format='SMS'` in the 
DireqtClient constructor, and then use the payload returned from `fetch` to
deliver ads:

```python
direqt = DireqtClient(API_KEY, ad_format="SMS")
result = direqt.fetch(ad_unit=AD_UNIT, msisdn=user_msisdn)
if result:
    send_sms_message(msisdn, result['payload'])
```

### Google RBM Network Transport

The SDK uses the Requests library <http://docs.python-requests.org/en/master/> as a network
transport to communicate with the Google RBM APIs on behalf of your application. If your 
application uses application default credentials (<https://developers.google.com/identity/protocols/application-default-credentials>),
then this should "just work" without any modification; the default credentials for your application
will be used for OAuth authentication.

If you are not using application default credentials, then you'll need to provide the SDK
with a Requests-compatible HTTP transport by specifying a `rbm_http` parameter to the 
constructor:

```python

my_requests = application_wrapper_around_requests()
direqt = DireqtClient(API_KEY, rbm_http=my_requests)
```

## Documentation

See <http://direqt-sdk-python.readthedocs.org/en/latest/> for documentation on using Direqt with Python.

Copyright (c) 2017-2018 Direqt Inc. All Rights Reserved.

