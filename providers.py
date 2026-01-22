"""
Image provider implementations for easy-wallpaper.

Provides abstract base class and concrete implementations for:
- Pexels (photography)
- Pixabay (illustrations)
- waifu.im (anime/waifu)
- nekos.moe (catgirl)
- Unsplash (photography)
- Wallhaven (anime/general)
- Bing (daily wallpapers)
- Picsum (random/seed)
"""

import os
import re
import random
from abc import ABC, abstractmethod
# pylint: disable=import-error
import requests
# pylint: enable=import-error


class ImageProvider(ABC):
    """Abstract base class for image providers."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the provider's display name."""

    @abstractmethod
    def get_description(self) -> str:
        """Return a brief description of the provider."""

    @abstractmethod
    def download_image(self, category: str, mood: str = "") -> bytes:
        """
        Download an image based on category and mood.

        Args:
            category: Image category/search term
            mood: Optional mood filter

        Returns:
            bytes: The image file content

        Raises:
            RuntimeError: If download fails
        """

    def set_resolution(self, resolution: str):
        """
        Set the target resolution for the image.
        Optional method for providers that support it.

        Args:
            resolution: Resolution string (e.g., '1920x1080')
        """


class PexelsProvider(ImageProvider):
    """Image provider for Pexels API."""

    def __init__(self):
        self.api_url = "https://api.pexels.com/v1/search"
        self.api_key = os.getenv("PEXELS_API_KEY", "")

    def get_name(self) -> str:
        return "Pexels"

    def get_description(self) -> str:
        return "High-quality images (no key required, 200 req/hour)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        """Download image from Pexels."""
        query = category
        if mood:
            query = f"{category} {mood}"

        headers = {}
        if self.api_key:
            headers["Authorization"] = self.api_key

        params = {"query": query, "per_page": 1}

        try:
            print(f"⏳ Downloading from Pexels ({query})...")
            if self.api_key:
                response = requests.get(self.api_url, headers=headers, params=params, timeout=15)
            else:
                raise RuntimeError(
                    "❌ PEXELS_API_KEY not set.\n"
                    "Get a free API key from: https://www.pexels.com/api/\n"
                    "Then run: export PEXELS_API_KEY='your-key-here'\n"
                    "\nAlternatively, use waifu.im (option 3) which requires no API key!"
                )
            response.raise_for_status()

            data = response.json()
            if not data.get("photos"):
                raise RuntimeError(f"❌ No images found for '{query}' on Pexels.")

            photo = data["photos"][0]
            image_url = photo["src"].get("original") or photo["src"].get("large")

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Pexels: {e}") from e
        except KeyError as exc:
            raise RuntimeError("❌ Unexpected Pexels API response format.") from exc


class PixabayProvider(ImageProvider):
    """Image provider for Pixabay API."""

    def __init__(self):
        self.api_url = "https://pixabay.com/api/"
        self.api_key = os.getenv("PIXABAY_API_KEY", "")

    def get_name(self) -> str:
        return "Pixabay"

    def get_description(self) -> str:
        return "Diverse images (requires API key, 100 req/hour)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        """Download image from Pixabay."""
        if not self.api_key:
            raise RuntimeError(
                "❌ PIXABAY_API_KEY not set.\n"
                "Get a free API key from: https://pixabay.com/api/\n"
                "Then run: export PIXABAY_API_KEY='your-key-here'"
            )

        query = category
        if mood:
            query = f"{category} {mood}"

        params = {
            "key": self.api_key,
            "q": query,
            "per_page": 1,
            "image_type": "photo",
        }

        try:
            print(f"⏳ Downloading from Pixabay ({query})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data.get("hits"):
                raise RuntimeError(f"❌ No images found for '{query}' on Pixabay.")

            image_data = data["hits"][0]
            image_url = image_data.get("largeImageURL") or image_data.get("webformatURL")

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Pixabay: {e}") from e
        except KeyError as exc:
            raise RuntimeError("❌ Unexpected Pixabay API response format.") from exc


class WaifuImProvider(ImageProvider):
    """Image provider for waifu.im API (anime/waifu images)."""

    def __init__(self):
        self.api_url = "https://api.waifu.im/search"

    def get_name(self) -> str:
        return "waifu.im"

    def get_description(self) -> str:
        return "Anime waifu images (no key required, unlimited)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        """Download image from waifu.im."""
        # Map categories to waifu.im tags
        waifu_tags = self._map_category_to_tags(category)

        params = {
            "included_tags": ",".join(waifu_tags),
            "is_nsfw": "false",
            "orientation": "landscape",
        }

        try:
            print(f"⏳ Downloading from waifu.im ({category})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data.get("images"):
                raise RuntimeError(f"❌ No images found for '{category}' on waifu.im.")

            image_url = data["images"][0]["url"]

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from waifu.im: {e}") from e
        except KeyError as exc:
            raise RuntimeError("❌ Unexpected waifu.im API response format.") from exc

    @staticmethod
    def _map_category_to_tags(category: str) -> list:
        """Map user category to waifu.im tags."""
        tag_map = {
            "nature": ["waifu"],
            "anime": ["waifu"],
            "waifu": ["waifu"],
            "maid": ["maid"],
            "miko": ["miko"],
            "oppai": ["oppai"],
            "uniform": ["uniform"],
            "kitsune": ["waifu"],
            "demon": ["demon"],
            "elf": ["elf"],
        }

        category_lower = category.lower()

        if category_lower in tag_map:
            return tag_map[category_lower]

        for key, value in tag_map.items():
            if key in category_lower:
                return value

        return ["waifu"]


class CatgirlProvider(ImageProvider):
    """Image provider for nekos.moe API (catgirl images)."""

    def __init__(self):
        self.api_url = "https://nekos.moe/api/v1/random/image"

    def get_name(self) -> str:
        return "nekos.moe"

    def get_description(self) -> str:
        return "Catgirl images (no key required, unlimited)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        """Download image from nekos.moe."""
        nsfw_param = self._map_category_to_nsfw(category)

        params = {}
        if nsfw_param is not None:
            params["nsfw"] = nsfw_param

        try:
            print(f"⏳ Downloading from nekos.moe ({category})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data.get("images"):
                raise RuntimeError(f"❌ No catgirl images found for '{category}' on nekos.moe.")

            image_id = data["images"][0]["id"]
            image_url = f"https://nekos.moe/image/{image_id}"

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from nekos.moe: {e}") from e
        except KeyError as exc:
            raise RuntimeError("❌ Unexpected nekos.moe API response format.") from exc

    @staticmethod
    def _map_category_to_nsfw(category: str) -> str | None:
        """Map user category to nekos.moe NSFW setting."""
        category_lower = category.lower()

        nsfw_map = {
            "safe": "false",
            "safe sfw": "false",
            "sfw": "false",
            "nsfw": "true",
            "lewd": "true",
            "mixed": None,
            "all": None,
        }

        if category_lower in nsfw_map:
            return nsfw_map[category_lower]

        for key, value in nsfw_map.items():
            if key in category_lower:
                return value

        return "false"


class UnsplashProvider(ImageProvider):
    """Image provider for Unsplash API."""

    def __init__(self):
        self.api_url = "https://api.unsplash.com/photos/random"
        self.api_key = os.getenv("UNSPLASH_ACCESS_KEY", "")

    def get_name(self) -> str:
        return "Unsplash"

    def get_description(self) -> str:
        return "Professional photos (requires Access Key, 50 req/hour)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        if not self.api_key:
            raise RuntimeError(
                "❌ UNSPLASH_ACCESS_KEY not set.\n"
                "Get a free Access Key from: https://unsplash.com/developers\n"
                "Then run: export UNSPLASH_ACCESS_KEY='your-key-here'"
            )

        query = category
        if mood:
            query = f"{category} {mood}"

        params = {"orientation": "landscape", "client_id": self.api_key}
        if query and query.lower() != "random":
            params["query"] = query

        try:
            print(f"⏳ Downloading from Unsplash ({query})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list):
                data = data[0]

            image_url = data["urls"]["raw"]

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Unsplash: {e}") from e


class WallhavenProvider(ImageProvider):
    """Image provider for Wallhaven API."""

    def __init__(self):
        self.api_url = "https://wallhaven.cc/api/v1/search"
        self.api_key = os.getenv("WALLHAVEN_API_KEY", "")

    def get_name(self) -> str:
        return "Wallhaven"

    def get_description(self) -> str:
        return "Anime & General wallpapers (API key optional)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = category
        if mood:
            query = f"{category} {mood}"

        params = {
            "q": query,
            "sorting": "random",
            "purity": "100", # SFW
        }
        if self.api_key:
            params["apikey"] = self.api_key

        try:
            print(f"⏳ Downloading from Wallhaven ({query})...")
            response = requests.get(
                self.api_url,
                params=params,
                timeout=15,
                headers={"User-Agent": "EasyWallpaper/1.0"}
            )
            response.raise_for_status()

            data = response.json()
            if not data.get("data"):
                raise RuntimeError(f"❌ No images found for '{query}' on Wallhaven.")

            image_url = data["data"][0]["path"]

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Wallhaven: {e}") from e


class BingProvider(ImageProvider):
    """Image provider for Bing Daily Wallpaper."""

    def __init__(self):
        self.api_url = "https://www.bing.com/HPImageArchive.aspx"

    def get_name(self) -> str:
        return "Bing"

    def get_description(self) -> str:
        return "Bing Daily Wallpaper (Today, Yesterday, etc.)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Map category to idx
        idx = 0
        cat_lower = category.lower()
        if "yesterday" in cat_lower:
            idx = 1
        elif "days ago" in cat_lower:
            try:
                match = re.search(r"(\d+)", cat_lower)
                if match:
                    idx = int(match.group(1))
            except ValueError:
                idx = 0

        idx = min(idx, 7)

        params = {
            "format": "js",
            "idx": idx,
            "n": 1,
            "mkt": "en-US"
        }

        try:
            print(f"⏳ Downloading from Bing ({category})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data.get("images"):
                raise RuntimeError("❌ Failed to get Bing image info.")

            url_base = data["images"][0]["url"]
            image_url = f"https://www.bing.com{url_base}"

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Bing: {e}") from e


class PicsumProvider(ImageProvider):
    """Image provider for Lorem Picsum."""

    def __init__(self):
        self.base_url = "https://picsum.photos"
        self.resolution = "1920x1080"

    def get_name(self) -> str:
        return "Picsum"

    def get_description(self) -> str:
        return "Random placeholder images (Resolution based)"

    def set_resolution(self, resolution: str):
        self.resolution = resolution

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Simple parsing of resolution string
        try:
            if "x" in self.resolution:
                parts = self.resolution.lower().split("x")
                if len(parts) >= 2:
                    width, height = parts[0], parts[1]
                else:
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            width, height = "1920", "1080"

        url = f"{self.base_url}/{width}/{height}"

        if category and category.lower() != "random":
            url = f"{self.base_url}/seed/{category}/{width}/{height}"

        try:
            print(f"⏳ Downloading from Picsum ({url})...")
            response = requests.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()

            print("✅ Download successful!")
            return response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Picsum: {e}") from e


class NasaApodProvider(ImageProvider):
    """Image provider for NASA APOD."""

    def __init__(self):
        self.api_url = "https://api.nasa.gov/planetary/apod"
        self.api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")

    def get_name(self) -> str:
        return "NASA APOD"

    def get_description(self) -> str:
        return "Astronomy Picture of the Day"

    def download_image(self, category: str, mood: str = "") -> bytes:
        params = {"api_key": self.api_key}

        if category.lower() == "random":
            params["count"] = 1

        try:
            print(f"⏳ Downloading from NASA APOD ({category})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            # If count is used, data is a list
            if isinstance(data, list):
                data = data[0]

            if data.get("media_type") != "image":
                raise RuntimeError("❌ Selected APOD is not an image (it might be a video).")

            image_url = data.get("hdurl") or data.get("url")

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from NASA APOD: {e}") from e


class TheCatApiProvider(ImageProvider):
    """Image provider for TheCatAPI."""

    def __init__(self):
        self.api_url = "https://api.thecatapi.com/v1/images/search"

    def get_name(self) -> str:
        return "TheCatAPI"

    def get_description(self) -> str:
        return "Random Cat Images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        try:
            print("⏳ Downloading from TheCatAPI...")
            response = requests.get(self.api_url, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data:
                raise RuntimeError("❌ No cat images found.")

            image_url = data[0]["url"]

            response = requests.get(image_url, timeout=15)
            response.raise_for_status()

            print("✅ Download successful!")
            return response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from TheCatAPI: {e}") from e


class TheDogApiProvider(ImageProvider):
    """Image provider for TheDogAPI."""

    def __init__(self):
        self.api_url = "https://api.thedogapi.com/v1/images/search"

    def get_name(self) -> str:
        return "TheDogAPI"

    def get_description(self) -> str:
        return "Random Dog Images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        try:
            print("⏳ Downloading from TheDogAPI...")
            response = requests.get(self.api_url, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data:
                raise RuntimeError("❌ No dog images found.")

            image_url = data[0]["url"]

            response = requests.get(image_url, timeout=15)
            response.raise_for_status()

            print("✅ Download successful!")
            return response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from TheDogAPI: {e}") from e


class MetMuseumProvider(ImageProvider):
    """Image provider for The Metropolitan Museum of Art."""

    def __init__(self):
        self.api_url = "https://collectionapi.metmuseum.org/public/collection/v1"

    def get_name(self) -> str:
        return "The Met"

    def get_description(self) -> str:
        return "Classic Art from The Met Museum"

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = category
        if category.lower() == "random":
            query = "painting"

        search_url = f"{self.api_url}/search"
        params = {"q": query, "hasImages": "true"}

        try:
            print(f"⏳ Searching The Met for '{query}'...")
            response = requests.get(search_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data.get("objectIDs"):
                raise RuntimeError(f"❌ No art found for '{query}'.")

            object_ids = data["objectIDs"]

            # Try up to 5 times to get an image
            for _ in range(5):
                object_id = random.choice(object_ids)
                object_url = f"{self.api_url}/objects/{object_id}"

                try:
                    obj_resp = requests.get(object_url, timeout=10)
                    obj_resp.raise_for_status()
                    obj_data = obj_resp.json()

                    image_url = obj_data.get("primaryImage")
                    if image_url:
                        print(f"⏳ Downloading '{obj_data.get('title')}'...")
                        response = requests.get(image_url, timeout=30)
                        response.raise_for_status()

                        print("✅ Download successful!")
                        return response.content
                except requests.exceptions.RequestException:
                    continue

            raise RuntimeError("❌ Failed to find a valid image after multiple attempts.")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to connect to The Met: {e}") from e
