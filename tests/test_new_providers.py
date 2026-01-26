import unittest
from unittest.mock import patch, MagicMock
from providers import (
    RedditProvider,
    DeviantArtProvider,
    KonachanProvider,
    FoodishProvider,
    FoxProvider,
    MemeProvider,
    ZenQuotesProvider,
    SafebooruProvider
)

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

    @patch('requests.Session.get')
    def test_fox_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"image": "http://example.com/fox.jpg"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = FoxProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Random")
            # Verify API call
            args, kwargs = mock_get.call_args_list[0]
            self.assertEqual(args[0], "https://randomfox.ca/floof/")
            # Verify download call
            mock_download.assert_called_with("http://example.com/fox.jpg")

    @patch('requests.Session.get')
    def test_meme_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"url": "http://example.com/meme.jpg"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = MemeProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("wholesomememes")
            # Verify API call
            args, kwargs = mock_get.call_args_list[0]
            self.assertIn("wholesomememes", args[0])
            mock_download.assert_called_with("http://example.com/meme.jpg")

    @patch('requests.Session.get')
    def test_zenquotes_provider(self, mock_get):
        # ZenQuotes does direct download, so _download_bytes is called with API URL
        provider = ZenQuotesProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Inspirational")
            mock_download.assert_called_with("https://zenquotes.io/api/image")

    @patch('requests.Session.get')
    def test_safebooru_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"file_url": "http://example.com/anime.jpg"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = SafebooruProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("anime")
            # Verify API call
            args, kwargs = mock_get.call_args_list[0]
            params = kwargs['params']
            self.assertEqual(params['page'], 'dapi')
            self.assertEqual(params['json'], '1')
            self.assertEqual(params['tags'], 'anime')
            mock_download.assert_called_with("http://example.com/anime.jpg")

if __name__ == '__main__':
    unittest.main()
