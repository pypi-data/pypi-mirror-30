import unittest


from .detector import _is_in_box

box1 = [{'x': 1, 'y': 2}, {'x': 7, 'y': 2}, {'x':1, 'y': 7}, {'x':7, 'y': 7}]
box2 = [{'x': 3, 'y': 5}, {'x': 3, 'y': 1}, {'x':9, 'y': 1}, {'x':9, 'y': 5}]

class DetecorTest(unittest.TestCase):
    
    def test_box(self):
        is_inside = _is_in_box(box1, box2)
        self.assertTrue(is_inside)


if __name__ == '__main__':
    unittest.main()