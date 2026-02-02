import unittest
from unittest.mock import patch, MagicMock
from providers import MinecraftSkinProvider, YugiohProvider, iTunesArtworkProvider

class TestAdditionalProviders(unittest.TestCase):

    @patch('requests.Session.get')
    def test_minecraft(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"image_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = MinecraftSkinProvider()

        # Test random
        provider.download_image("random")
        args, kwargs = mock_get.call_args
        # Should be one of the famous players
        self.assertIn("minotar.net/armor/body", args[0])
        self.assertTrue(args[0].endswith("/1920.png"))

        # Test specific
        provider.download_image("Steve")
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://minotar.net/armor/body/Steve/1920.png")

    @patch('requests.Session.get')
    def test_yugioh(self, mock_get):
        mock_response = MagicMock()
        # Mock random response
        mock_response.json.return_value = {"data": [{"card_images": [{"image_url": "http://example.com/card.jpg"}], "name": "Dark Magician"}]}
        mock_response.content = b"image_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = YugiohProvider()

        # Test random
        provider.download_image("random")
        # Call 0: API, Call 1: Image
        self.assertEqual(mock_get.call_count, 2)
        args_api, _ = mock_get.call_args_list[0]
        self.assertIn("randomcard.php", args_api[0])

    @patch('requests.Session.get')
    def test_itunes(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{
                "artworkUrl100": "http://example.com/100x100bb.jpg",
                "trackName": "Song",
                "artistName": "Artist"
            }]
        }
        mock_response.content = b"image_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = iTunesArtworkProvider()

        # Test search
        provider.download_image("Beatles")
        # Call 0: API, Call 1: Image
        self.assertEqual(mock_get.call_count, 2)
        args_api, kwargs_api = mock_get.call_args_list[0]
        self.assertIn("search", args_api[0])
        self.assertEqual(kwargs_api['params']['term'], "Beatles")

        # Check image URL hack
        args_img, _ = mock_get.call_args_list[1]
        self.assertEqual(args_img[0], "http://example.com/10000x10000bb.jpg")

if __name__ == '__main__':
    unittest.main()
