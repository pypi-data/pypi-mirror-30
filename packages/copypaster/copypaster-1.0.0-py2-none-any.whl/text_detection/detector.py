"""
Handles the detection within an image
"""

def _is_in_box(target, big_box):
    big_top = None
    big_bottom = None
    big_left = None
    big_right = None

    for i in big_box:
        if (not big_top) or i['y'] > big_top:
            big_top = i['y']
        
        if (not big_bottom) or i['y'] < big_bottom:
            big_bottom = i['y']
        
        if (not big_left) or i['x'] < big_left:
            big_left = i['x']
        
        if (not big_right) or i['x'] > big_right:
            big_right = i['x']
        

    for i in target:
        if big_left < i['x'] < big_right and  big_bottom < i['y'] < big_top:
            return True

    return False

WHITESPACES = {
    "SPACE": ' ',
    'EOL_SURE_SPACE': '\n',
    '': '',
}

def _parse_symbol(symbol):
    whitespace = symbol.get('property', {}).get('detectedBreak', {}).get('type', '')
    return "{0}{1}".format(symbol['text'], WHITESPACES.get(whitespace, whitespace))

class Detector():
    
    def __init__(self, detection):
        self.symbols = []

        for page in detection.get("pages", []):
            for block in page["blocks"]:
                for paragraph in block["paragraphs"]:
                    for word in paragraph["words"]:
                        for symbol in word["symbols"]:
                            whitespace = symbol.get('property', {}).get('detectedBreak', {}).get('type', '')
                            if whitespace:
                                print(whitespace)
                            self.symbols.append(symbol)

    def detect(self, vertices):

        selected_chars = [_parse_symbol(symbol) for symbol in self.symbols if _is_in_box(symbol["boundingBox"]["vertices"], vertices)]

        text = ''.join(selected_chars)
        return text