"""Client library for Direqt Ads API."""
import json
import logging
import uuid
import hashlib
import requests

from util import detect_gae
from . import rbm

logger = logging.getLogger(__name__)

_DEFAULT_ENDPOINT = 'https://ads.direqt.io'
_DEFAULT_USER_AGENT = 'unknown'

_AD_FORMAT_RBM10 = 'RBMV1.0'
_AD_FORMAT_SMS = 'SMS'
_DEFAULT_AD_FORMAT = _AD_FORMAT_RBM10
_VALID_AD_FORMATS = [_AD_FORMAT_RBM10, _AD_FORMAT_SMS]

_DEFAULT_RBM_ENDPOINT = 'https://rcsbusinessmessaging.googleapis.com'


class DireqtClient(object):
    """Client for the Direqt ad server."""

    def __init__(self, api_key, ad_format=_DEFAULT_AD_FORMAT, user_agent=_DEFAULT_USER_AGENT, **kwargs):
        """Initializes a DireqtClient.

        Args:
            api_key: A string containing your Direqt API key.
            format: One of 'RBMV1.0' or 'SMS'
            user_agent: An arbitrary string containing only ASCII characters
                that will be used to identify your application. If not set,
                defaults to "unknown".
            **kwargs: Optional keyword arguments.

        Keyword Arguments:
            None defined.
        """
        super(DireqtClient, self).__init__()

        if ad_format not in _VALID_AD_FORMATS:
            raise NotImplementedError(
                'The provided ad format "%s" is invalid. Accepted formats are: %s'
                % (format, _VALID_AD_FORMATS))

        if detect_gae():
            import requests_toolbelt.adapters.appengine
            requests_toolbelt.adapters.appengine.monkeypatch()

        self.api_key = api_key
        self.fmt = ad_format
        self.user_agent = user_agent
        self.endpoint = kwargs.get('endpoint', _DEFAULT_ENDPOINT)               # private
        self.http = kwargs.get('http', requests)                                # private
        self.rbm_endpoint = kwargs.get('rbm_endpoint', _DEFAULT_RBM_ENDPOINT)   # private
        self.rbm_http = kwargs.get('rbm_http', rbm.http)

    def fetch(self, ad_unit, msisdn, targeting=None):
        """Fetch an ad from the Direqt Ads API.

        If no ad is available, this method returns False.

        If the ad_format specified in the constructor was "RBMV1.0" this method
        will handle the sending of any messages necessary to deliver the
        advertisement.

        If the ad_format is "SMS", this method will return an object containing
        the 'message_id' and 'payload' of the message that should be sent to the
        subscriber using the application's messaging platform.

        Args:
            ad_unit: An ad unit code configured in your project.
            msisdn: A string identifying the current user.
            targeting: An array of tuples specifying name/value pairs for targeting
        """
        targeting = targeting or {}
        params = {
            'key': self.api_key,
            'format': self.fmt,
            'adUnit': ad_unit,
            'subscriber': hashlib.md5(msisdn).hexdigest(),
            'targeting': json.dumps(targeting)
        }

        url = self.endpoint + "/fetch"
        response = self.http.post(url, params=params, data={})
        if response.status_code == 200:
            body = response.json()
            return self._process_fetch_result(msisdn, body)
        else:
            try:
                errormsg = "Direqt fetch error: {0}".format(json.dumps(response.json()))
            except:
                errormsg = "Direqt fetch error: status_code={0} reason={1}".format(response.status_code, response.reason)

            logger.debug(errormsg)

        return False

    def notify_suggested_reply(self, msisdn, postback_data):
        """Notify of a suggested reply from a user.

        This method should be called whenever your agent is notified that a user
        has responded to a suggestion from an earlier message.

        Suggested replies are only relevant for ad_format "RBMV1.0".

        If the suggested reply was handled by Direqt, this method will return True.
        Otherwise, returns False.
        :type postback_data: str
        """
        if not postback_data or not postback_data.startswith('@direqt'):
            return False

        params = {
            'key': self.api_key,
            'format': self.fmt,
            'postbackData': postback_data
        }

        url = self.endpoint + "/interact"
        response = self.http.post(url, params=params, data={})
        if response.status_code == 200:
            body = response.json()
            self._process_fetch_result(msisdn, body)    # return code ignored

        return True

    def _process_fetch_result(self, msisdn, body):
        if self.fmt == _AD_FORMAT_SMS:
            payload = body['payload'] if 'payload' in body else None
            message_id = body['messageId'] if 'messageId' in body else None
            properties = body['properties'] if 'properties' in body else {}
            if not payload or not message_id:
                return False

            response = {
                'payload': payload,
                'message_id': message_id,
                'properties': properties
            }

            return response

        media = body['media'] if 'media' in body else []
        payload = body['payload'] if 'payload' in body else None

        if not media and not payload:
            logger.debug("Unexpected response from Direqt fetch.")
            return False

        logger.info("Received payload: " + (payload or '<none>'))

        for m in media:
            uri = self._upload_media(m['file_url'],
                                     thumbnail_url=m['thumbnail_url'],
                                     content_description=m['content_description'])
            if not uri:
                logger.error('Failed to upload media file.')
                return False

            if payload:
                payload = payload.replace(m['file_url'], uri)

        return self._deliver_payload(msisdn, uuid.uuid4(), payload)

    def _deliver_payload(self, msisdn, message_id, payload):
        url = self.rbm_endpoint + "/v1/phones/{0}/agentMessages?messageId={1}".format(msisdn, message_id)

        logger.info("Posting agent message {0} for {1}".format(message_id, msisdn))
        logger.info("  url = " + url)
        logger.info("  payload = " + payload)

        response = self.rbm_http.post(url, data=payload, headers={'Content-Type': 'application/json'})

        logger.info("Received response from " + url)
        logger.info("  status_code: " + str(response.status_code))
        logger.info("  response: " + json.dumps(response.json()))

        success = response.status_code == 200
        if not success:
            logger.error("Post of agent message failed!")

        return success

    def _upload_media(self, file_url, thumbnail_url=None, content_description=None):
        url = self.rbm_endpoint + "/v1/files"
        request = {'fileUrl': file_url}
        if thumbnail_url is not None:
            request['thumbnailUrl'] = thumbnail_url
        if content_description is not None:
            request['contentDescription'] = content_description

        logger.info("Uploading media file")
        logger.info("  url = " + url)
        logger.info("  fileUrl = " + file_url)
        logger.info("  thumbnailUrl = " + thumbnail_url)
        logger.info("  contentDescription = " + content_description)

        response = self.rbm_http.post(url, json=request)

        logger.info("Received response from " + url)
        logger.info("  status_code: " + str(response.status_code))
        logger.info("  response: " + json.dumps(response.json()))

        success = response.status_code == 200
        if not success:
            logger.error("Post of file upload failed!")
            return None

        response_json = response.json()
        if not response_json or 'name' not in response_json:
            logger.error("Unexpected response from file upload.")
            return None

        return response_json['name']
