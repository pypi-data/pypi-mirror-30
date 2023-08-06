"""
This exists for testing and dev work on the api caller
"""
from .api import VisionApi

from .detector import Detector

if __name__ == '__main__':
    api = VisionApi()


    with open('test_images/blank.png', 'rb' ) as img_file:
        image = img_file.read()
    api_response = api.detect_text(image)
    print(api_response)

    vertices = [
        {'x': 20, 'y': 15},
        {'x': 20, 'y': 70},
        {'x': 100, 'y': 15},
        {'x': 100, 'y': 70},
    ]

    detector = Detector(api_response)

    result = detector.detect(vertices)
    print(result)


