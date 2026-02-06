import unittest
from unittest.mock import patch, MagicMock
from providers import ArtInstituteProvider, RickAndMortyProvider, OpenLibraryProvider, RandomMetaProvider

class TestNewProviders(unittest.TestCase):

    @patch('requests.Session.get')
    def test_art_institute_provider(self, mock_get):
        # Setup mock
        mock_response_search = MagicMock()
        mock_response_search.json.return_value = {
            "data": [{"id": 123, "title": "Test Art", "image_id": "img123"}],
            "config": {"iiif_url": "https://iiif.example.com"}
        }
        mock_response_search.raise_for_status.return_value = None

        mock_response_image = MagicMock()
        mock_response_image.content = b"fake_image_bytes"
        mock_response_image.raise_for_status.return_value = None

        # Chain requests: 1st call for search, 2nd call for image
        mock_get.side_effect = [mock_response_search, mock_response_image]

        provider = ArtInstituteProvider()
        image_bytes = provider.download_image("Impressionism")

        self.assertEqual(image_bytes, b"fake_image_bytes")

        # Verify search URL
        args, kwargs = mock_get.call_args_list[0]
        self.assertIn("artic.edu/api/v1/artworks/search", args[0])
        self.assertEqual(kwargs['params']['q'], "Impressionism")

        # Verify image URL
        args_img, _ = mock_get.call_args_list[1]
        expected_url = "https://iiif.example.com/img123/full/1600,/0/default.jpg"
        self.assertEqual(args_img[0], expected_url)

    @patch('requests.Session.get')
    def test_rick_and_morty_provider(self, mock_get):
        mock_response_search = MagicMock()
        mock_response_search.json.return_value = {
            "results": [{"name": "Rick", "image": "http://example.com/rick.jpg"}]
        }
        mock_response_search.raise_for_status.return_value = None

        mock_response_image = MagicMock()
        mock_response_image.content = b"rick_bytes"
        mock_response_image.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_search, mock_response_image]

        provider = RickAndMortyProvider()
        image_bytes = provider.download_image("Rick")

        self.assertEqual(image_bytes, b"rick_bytes")

        # Verify search
        args, kwargs = mock_get.call_args_list[0]
        self.assertEqual(kwargs['params']['name'], "Rick")

    @patch('requests.Session.get')
    def test_open_library_provider(self, mock_get):
        mock_response_search = MagicMock()
        mock_response_search.json.return_value = {
            "docs": [{"title": "LOTR", "cover_i": 999}]
        }
        mock_response_search.raise_for_status.return_value = None

        mock_response_image = MagicMock()
        mock_response_image.content = b"book_bytes"
        mock_response_image.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_search, mock_response_image]

        provider = OpenLibraryProvider()
        image_bytes = provider.download_image("Tolkien")

        self.assertEqual(image_bytes, b"book_bytes")

        # Verify image URL
        args_img, _ = mock_get.call_args_list[1]
        self.assertEqual(args_img[0], "https://covers.openlibrary.org/b/id/999-L.jpg")

    def test_random_meta_provider(self):
        # Mock dependencies
        mock_provider = MagicMock()
        mock_provider.get_name.return_value = "MockProvider"
        mock_provider.download_image.return_value = b"meta_bytes"

        providers = {"1": mock_provider, "0": None} # 0 is self
        categories = {"MockProvider": ["Cat1", "Cat2"]}
        moods = {"MockProvider": ["Mood1"]}

        meta = RandomMetaProvider(providers, categories, moods)

        # Patch random to behave deterministically
        with patch('random.choice') as mock_random:
            # First random.choice picks provider key (valid_keys)
            # Second random.choice picks category (if category is random)
            # Third random.choice picks mood (if mood is empty)

            # Since we iterate dict keys, order might vary. But we only have one valid key "1".
            # So random.choice(["1"]) -> "1"

            # Case 1: Random category
            mock_random.side_effect = ["1", "Cat2", "Mood1"]

            result = meta.download_image("Random", "")

            self.assertEqual(result, b"meta_bytes")
            mock_provider.download_image.assert_called_with("Cat2", "Mood1")

if __name__ == '__main__':
    unittest.main()
