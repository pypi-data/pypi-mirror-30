"""

This is from https://github.com/GoogleCloudPlatform/cloud-vision/blob/master/python/text/textindex.py
"""
import base64

from googleapiclient import discovery, errors
from oauth2client.client import GoogleCredentials


DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'  # noqa
BATCH_SIZE = 10


class VisionApi:
    """Construct and use the Google Vision API service."""

    def __init__(self, api_discovery_file='vision_api.json'):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = discovery.build(
            'vision', 'v1', credentials=self.credentials,
            discoveryServiceUrl=DISCOVERY_URL)

    def detect_text(self, image, num_retries=3, max_results=6):
        """Uses the Vision API to detect text in the given file.
        """

        image_request = {
            'image': {
                'content': base64.b64encode(image).decode('UTF-8')
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': max_results,
            }]
        }
        request = self.service.images().annotate( #pylint: disable no-member
            body={'requests': [image_request]})

        try:
            responses = request.execute(num_retries=num_retries)
            if 'responses' not in responses:
                return {}
            full_text_response = {}
            response = responses['responses'][0]
            if 'error' in response:
                print("API Error: %s" % (
                        response['error']['message']
                        if 'message' in response['error']
                        else ''))
            if 'fullTextAnnotation' in response:
                full_text_response = response['fullTextAnnotation']
            else:
                full_text_response = {}
            return full_text_response
        except errors.HttpError as e:
            print("Http Error: %s" % e)
        except KeyError as e2:
            print("Key error: %s" % e2)
