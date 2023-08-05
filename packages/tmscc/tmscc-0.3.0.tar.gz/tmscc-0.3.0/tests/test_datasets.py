import unittest

from tmscc import datasets


class TestDatasets(unittest.TestCase):
    
    def setUp(self):
        self.profile, self.labels = datasets.load_klein()

    def test_shape(self):
        self.assertEqual(
            self.profile.shape, (900, 1000))
