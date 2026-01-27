import unittest
from unittest.mock import patch, MagicMock
from providers import (
    XKCDProvider,
    DogCeoProvider,
    ImgFlipProvider,
    CoffeeProvider,
    CataasProvider,
    PlaceBearProvider,
    PlaceDogProvider,
    RobohashProvider
)

class TestAdditionalProviders(unittest.TestCase):

    @patch('requests.Session.get')
    def test_xkcd_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"img": "https://imgs.xkcd.com/comics/test.png", "num": 100}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = XKCDProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            # Test Current
            provider.download_image("Current")
            mock_download.assert_called_with("https://imgs.xkcd.com/comics/test.png")

    @patch('requests.Session.get')
    def test_dogceo_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "https://images.dog.ceo/test.jpg"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = DogCeoProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Random")
            mock_download.assert_called_with("https://images.dog.ceo/test.jpg")

    @patch('requests.Session.get')
    def test_imgflip_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "memes": [{"url": "https://i.imgflip.com/test.jpg"}]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = ImgFlipProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Random")
            mock_download.assert_called_with("https://i.imgflip.com/test.jpg")

    @patch('requests.Session.get')
    def test_coffee_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"file": "https://coffee.alexflipnote.dev/test.jpg"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = CoffeeProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Random")
            mock_download.assert_called_with("https://coffee.alexflipnote.dev/test.jpg")

    @patch('requests.Session.get')
    def test_cataas_provider(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"url": "/cat/test_id"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = CataasProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Random")
            mock_download.assert_called_with("https://cataas.com/cat/test_id")

    @patch('requests.Session.get')
    def test_placebear_provider(self, mock_get):
        provider = PlaceBearProvider()
        provider.set_resolution("800x600")
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Random")
            mock_download.assert_called_with("https://placebear.com/800/600")

    @patch('requests.Session.get')
    def test_placedog_provider(self, mock_get):
        provider = PlaceDogProvider()
        provider.set_resolution("800x600")
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            provider.download_image("Random")
            mock_download.assert_called_with("https://placedog.net/800/600?random")

    @patch('requests.Session.get')
    def test_robohash_provider(self, mock_get):
        provider = RobohashProvider()
        with patch.object(provider, '_download_bytes', return_value=b'fakedata') as mock_download:
            # Test default
            provider.download_image("TestSeed", "robots")
            mock_download.assert_called_with("https://robohash.org/TestSeed.png?set=set1&size=1024x1024")

            # Test monsters
            provider.download_image("TestSeed", "monsters")
            mock_download.assert_called_with("https://robohash.org/TestSeed.png?set=set2&size=1024x1024")

            # Test cats
            provider.download_image("TestSeed", "cats")
            mock_download.assert_called_with("https://robohash.org/TestSeed.png?set=set4&size=1024x1024")

if __name__ == '__main__':
    unittest.main()
