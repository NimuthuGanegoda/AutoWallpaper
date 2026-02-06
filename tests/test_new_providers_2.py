import unittest
from unittest.mock import patch, MagicMock
from providers import CountryFlagsProvider, AmiiboApiProvider, CoinCapProvider, DiceBearProvider

class TestNewProviders2(unittest.TestCase):

    @patch('requests.Session.get')
    def test_country_flags(self, mock_get):
        provider = CountryFlagsProvider()

        # Test basic code
        # _download_bytes calls session.get(url)
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        data = provider.download_image("us")
        self.assertEqual(data, b"fake_image_data")

        # Verify URL
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://flagcdn.com/w2560/us.png")

        # Test random
        provider.download_image("random")
        # Just check it didn't crash and called URL
        self.assertTrue(mock_get.called)

    @patch('requests.Session.get')
    def test_amiibo(self, mock_get):
        provider = AmiiboApiProvider()

        # Mock API response
        mock_api_response = MagicMock()
        mock_api_response.json.return_value = {
            "amiibo": [
                {"name": "Mario", "gameSeries": "Super Mario", "image": "http://example.com/mario.png"}
            ]
        }
        mock_api_response.raise_for_status.return_value = None

        # Mock Image response
        mock_img_response = MagicMock()
        mock_img_response.content = b"mario_bytes"
        mock_img_response.raise_for_status.return_value = None

        # Side effect to return different mocks based on URL
        def side_effect(*args, **kwargs):
            if "amiiboapi.com" in args[0]:
                return mock_api_response
            else:
                return mock_img_response

        mock_get.side_effect = side_effect

        data = provider.download_image("Mario")
        self.assertEqual(data, b"mario_bytes")

    @patch('requests.Session.get')
    def test_coincap(self, mock_get):
        provider = CoinCapProvider()

        mock_response = MagicMock()
        mock_response.content = b"crypto_bytes"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        data = provider.download_image("BTC")
        self.assertEqual(data, b"crypto_bytes")

        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://assets.coincap.io/assets/icons/btc@2x.png")

    @patch('requests.Session.get')
    def test_dicebear(self, mock_get):
        provider = DiceBearProvider()

        mock_response = MagicMock()
        mock_response.content = b"avatar_bytes"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Specific style
        data = provider.download_image("bottts")
        self.assertEqual(data, b"avatar_bytes")

        args, kwargs = mock_get.call_args
        self.assertIn("api.dicebear.com/7.x/bottts/png", args[0])

        # Random style
        provider.download_image("random")
        self.assertTrue(mock_get.called)

if __name__ == '__main__':
    unittest.main()
