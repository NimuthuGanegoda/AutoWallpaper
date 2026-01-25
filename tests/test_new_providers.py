import unittest
from unittest.mock import patch, MagicMock
from providers import RedditProvider, DeviantArtProvider, KonachanProvider, FoodishProvider

class TestNewProviders(unittest.TestCase):

    @patch('requests.Session.get')
    def test_reddit_provider(self, mock_get):
        # Mock Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "url": "https://example.com/image.jpg"
                        }
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = RedditProvider()
        # Mock download_bytes to avoid actual download
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("wallpapers")
            mock_download.assert_called_with("https://example.com/image.jpg")

    @patch('requests.Session.get')
    def test_foodish_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"image": "https://foodish-api.com/images/pizza/pizza1.jpg"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = FoodishProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("pizza")
            mock_download.assert_called_with("https://foodish-api.com/images/pizza/pizza1.jpg")

    @patch('requests.Session.get')
    def test_konachan_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "file_url": "https://konachan.net/image.jpg",
                "rating": "s"
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = KonachanProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("random")
            mock_download.assert_called_with("https://konachan.net/image.jpg")

if __name__ == '__main__':
    unittest.main()
