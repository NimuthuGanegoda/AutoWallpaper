import unittest
from unittest.mock import patch, MagicMock
from providers import UnsplashProvider, WallhavenProvider

class TestProviders(unittest.TestCase):

    @patch('requests.Session.get')
    def test_unsplash_orientation(self, mock_get):
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"urls": {"raw": "http://example.com/image.jpg"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = UnsplashProvider()
        provider.api_key = "test_key"

        # Test default behavior
        provider.download_image("nature")
        # Call 0 is API, Call 1 is Image
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs['params']
        self.assertEqual(params['orientation'], 'landscape')

        # Test with resolution (Portrait)
        provider.set_resolution("1080x1920") # Portrait
        provider.download_image("nature")
        # Call 2 is API, Call 3 is Image
        args, kwargs = mock_get.call_args_list[2]
        params = kwargs['params']
        self.assertEqual(params['orientation'], 'portrait')

        # Test with resolution (Squarish)
        provider.set_resolution("1000x1000") # Squarish
        provider.download_image("nature")
        # Call 4 is API, Call 5 is Image
        args, kwargs = mock_get.call_args_list[4]
        params = kwargs['params']
        self.assertEqual(params['orientation'], 'squarish')

    @patch('requests.Session.get')
    def test_wallhaven_ratios(self, mock_get):
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"path": "http://example.com/image.jpg"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = WallhavenProvider()

        # Test default
        provider.download_image("anime")
        # Call 0 is API, Call 1 is Image
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs['params']
        self.assertNotIn('ratios', params)

        # Test with resolution 1920x1080 (16x9)
        provider.set_resolution("1920x1080")
        provider.download_image("anime")
        # Call 2 is API, Call 3 is Image
        args, kwargs = mock_get.call_args_list[2]
        params = kwargs['params']
        self.assertEqual(params['ratios'], '16x9')

        # Test with resolution 21x9 (Ultrawide) e.g. 2560x1080 -> 64x27 (wait, 2560/40=64, 1080/40=27. 64x27 is exact ratio)
        # Wallhaven might expect simplified ratios or just common ones. The API says "Resolution ratio... (e.g. 16x9, 9x16)".
        # Let's try 2560x1440 which is 16x9.
        provider.set_resolution("2560x1440")
        provider.download_image("anime")
        # Call 4 is API, Call 5 is Image
        args, kwargs = mock_get.call_args_list[4]
        params = kwargs['params']
        self.assertEqual(params['ratios'], '16x9')

if __name__ == '__main__':
    unittest.main()
