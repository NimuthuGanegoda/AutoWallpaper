import unittest
from unittest.mock import patch, MagicMock
from providers import WikipediaProvider, LibraryOfCongressProvider, FlickrProvider

class TestFinalProviders(unittest.TestCase):

    @patch('requests.Session.get')
    def test_wikipedia(self, mock_get):
        # Mock API response for search
        mock_api_resp = MagicMock()
        mock_api_resp.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Cat",
                        "original": {"source": "http://example.com/cat.jpg"}
                    }
                }
            }
        }
        mock_api_resp.raise_for_status.return_value = None

        # Mock Image response
        mock_img_resp = MagicMock()
        mock_img_resp.content = b"fake_image_bytes"
        mock_img_resp.raise_for_status.return_value = None

        mock_get.side_effect = [mock_api_resp, mock_img_resp]

        provider = WikipediaProvider()
        data = provider.download_image("Cat")

        self.assertEqual(data, b"fake_image_bytes")
        # Verify API call
        args, kwargs = mock_get.call_args_list[0]
        self.assertEqual(kwargs['params']['titles'], 'Cat')

    @patch('requests.Session.get')
    def test_wikipedia_random(self, mock_get):
        # Mock API response for random
        mock_api_resp = MagicMock()
        mock_api_resp.json.return_value = {
            "query": {
                "pages": {
                    "456": {
                        "title": "Random Page",
                        "original": {"source": "http://example.com/random.png"}
                    }
                }
            }
        }
        mock_api_resp.raise_for_status.return_value = None

        mock_img_resp = MagicMock()
        mock_img_resp.content = b"fake_image_bytes"
        mock_img_resp.raise_for_status.return_value = None

        mock_get.side_effect = [mock_api_resp, mock_img_resp]

        provider = WikipediaProvider()
        data = provider.download_image("Random")

        self.assertEqual(data, b"fake_image_bytes")
        args, kwargs = mock_get.call_args_list[0]
        self.assertEqual(kwargs['params']['generator'], 'random')

    @patch('requests.Session.get')
    def test_loc(self, mock_get):
        # Mock API response
        mock_api_resp = MagicMock()
        mock_api_resp.json.return_value = {
            "results": [
                {
                    "title": "Civil War Photo",
                    "image_url": ["http://example.com/small.jpg", "http://example.com/large.jpg"]
                }
            ]
        }
        mock_api_resp.raise_for_status.return_value = None

        mock_img_resp = MagicMock()
        mock_img_resp.content = b"fake_image_bytes"
        mock_img_resp.raise_for_status.return_value = None

        mock_get.side_effect = [mock_api_resp, mock_img_resp]

        provider = LibraryOfCongressProvider()
        data = provider.download_image("Civil War")

        self.assertEqual(data, b"fake_image_bytes")
        # Check that it picked the large jpg
        args, kwargs = mock_get.call_args_list[1]
        self.assertEqual(args[0], "http://example.com/large.jpg")

    @patch('requests.Session.get')
    def test_flickr(self, mock_get):
        # Mock API response
        mock_api_resp = MagicMock()
        mock_api_resp.json.return_value = {
            "items": [
                {
                    "title": "Forest",
                    "media": {"m": "http://example.com/forest_m.jpg"}
                }
            ]
        }
        mock_api_resp.raise_for_status.return_value = None

        mock_img_resp = MagicMock()
        mock_img_resp.content = b"fake_image_bytes"
        mock_img_resp.raise_for_status.return_value = None

        mock_get.side_effect = [mock_api_resp, mock_img_resp]

        provider = FlickrProvider()
        data = provider.download_image("Nature")

        self.assertEqual(data, b"fake_image_bytes")
        # Check URL upgrade from _m to _b
        args, kwargs = mock_get.call_args_list[1]
        self.assertEqual(args[0], "http://example.com/forest_b.jpg")

if __name__ == '__main__':
    unittest.main()
