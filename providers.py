"""
Image provider implementations for easy-wallpaper.

Provides abstract base class and concrete implementations for:
- Pexels (photography)
- Pixabay (illustrations)
- waifu.im (anime/waifu)
- nekos.moe (catgirl)
- Unsplash (photography)
- Wallhaven (anime/wallpaper)
- Bing (daily wallpapers)
- Picsum (random/seeded placeholders)
"""

import os
from abc import ABC, abstractmethod
import requests
import random


class ImageProvider(ABC):
    """Abstract base class for image providers."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the provider's display name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a brief description of the provider."""
        pass
    
    @abstractmethod
    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
        """
        Download an image based on category and mood.
        
        Args:
            category: Image category/search term
            mood: Optional mood filter
            resolution: Desired resolution (e.g., "1920x1080")
        
        Returns:
            bytes: The image file content
        
        Raises:
            RuntimeError: If download fails
        """
        pass


class PexelsProvider(ImageProvider):
    """Image provider for Pexels API."""
    
    def __init__(self):
        self.api_url = "https://api.pexels.com/v1/search"
        self.api_key = os.getenv("PEXELS_API_KEY", "")
    
    def get_name(self) -> str:
        return "Pexels"
    
    def get_description(self) -> str:
        return "High-quality images (no key required, 200 req/hour)"
    
    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
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
            raise RuntimeError(f"❌ Failed to download from Pexels: {e}")
        except KeyError:
            raise RuntimeError("❌ Unexpected Pexels API response format.")


class PixabayProvider(ImageProvider):
    """Image provider for Pixabay API."""
    
    def __init__(self):
        self.api_url = "https://pixabay.com/api/"
        self.api_key = os.getenv("PIXABAY_API_KEY", "")
    
    def get_name(self) -> str:
        return "Pixabay"
    
    def get_description(self) -> str:
        return "Diverse images (requires API key, 100 req/hour)"
    
    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
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
            "per_page": 20,
            "image_type": "photo",
        }
        
        try:
            print(f"⏳ Downloading from Pixabay ({query})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("hits"):
                raise RuntimeError(f"❌ No images found for '{query}' on Pixabay.")
            
            hits = data["hits"]
            image_data = random.choice(hits)

            image_url = image_data.get("largeImageURL") or image_data.get("webformatURL")
            
            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()
            
            print("✅ Download successful!")
            return image_response.content
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Pixabay: {e}")
        except KeyError:
            raise RuntimeError("❌ Unexpected Pixabay API response format.")


class WaifuImProvider(ImageProvider):
    """Image provider for waifu.im API (anime/waifu images)."""
    
    def __init__(self):
        self.api_url = "https://api.waifu.im/search"
    
    def get_name(self) -> str:
        return "waifu.im"
    
    def get_description(self) -> str:
        return "Anime waifu images (no key required, unlimited)"
    
    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
        """Download image from waifu.im."""
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
            raise RuntimeError(f"❌ Failed to download from waifu.im: {e}")
        except KeyError:
            raise RuntimeError("❌ Unexpected waifu.im API response format.")
    
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
            "random": ["waifu"],
        }
        
        category_lower = category.lower()
        
        if category_lower in tag_map:
            return tag_map[category_lower]
        
        for key in tag_map:
            if key in category_lower:
                return tag_map[key]
        
        return ["waifu"]


class CatgirlProvider(ImageProvider):
    """Image provider for nekos.moe API (catgirl images)."""
    
    def __init__(self):
        self.api_url = "https://nekos.moe/api/v1/random/image"
    
    def get_name(self) -> str:
        return "nekos.moe"
    
    def get_description(self) -> str:
        return "Catgirl images (no key required, unlimited)"
    
    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
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
            raise RuntimeError(f"❌ Failed to download from nekos.moe: {e}")
        except KeyError:
            raise RuntimeError("❌ Unexpected nekos.moe API response format.")
    
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
            "random": "false",
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
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY", "")

    def get_name(self) -> str:
        return "Unsplash"

    def get_description(self) -> str:
        return "Professional photos (requires access key)"

    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
        """Download image from Unsplash."""
        if not self.access_key:
            raise RuntimeError(
                "❌ UNSPLASH_ACCESS_KEY not set.\n"
                "Get a free API key from: https://unsplash.com/developers\n"
                "Then run: export UNSPLASH_ACCESS_KEY='your-key-here'"
            )

        query = category
        if mood:
            query = f"{category} {mood}"

        headers = {
            "Authorization": f"Client-ID {self.access_key}"
        }

        params = {
            "orientation": "landscape",
        }

        if category.lower() != "random":
            params["query"] = query

        try:
            print(f"⏳ Downloading from Unsplash ({query})...")
            response = requests.get(self.api_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            image_url = data["urls"]["regular"]

            # Use raw URL with parameters for specific resolution if provided
            if resolution and "raw" in data["urls"]:
                try:
                    w, h = resolution.split('x')
                    image_url = f"{data['urls']['raw']}&w={w}&h={h}&fit=crop"
                except ValueError:
                    # Fallback to full if resolution parse fails
                    image_url = data["urls"]["full"]

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Unsplash: {e}")
        except KeyError:
            raise RuntimeError("❌ Unexpected Unsplash API response format.")


class WallhavenProvider(ImageProvider):
    """Image provider for Wallhaven API."""

    def __init__(self):
        self.api_url = "https://wallhaven.cc/api/v1/search"
        self.api_key = os.getenv("WALLHAVEN_API_KEY", "")

    def get_name(self) -> str:
        return "Wallhaven"

    def get_description(self) -> str:
        return "Anime & General Wallpapers (optional key)"

    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
        """Download image from Wallhaven."""
        query = category
        if mood:
            query = f"{category} {mood}"

        params = {
            "q": query,
            "sorting": "random",
        }

        if self.api_key:
            params["apikey"] = self.api_key

        params["purity"] = "100"

        try:
            print(f"⏳ Downloading from Wallhaven ({query})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data.get("data"):
                raise RuntimeError(f"❌ No images found for '{query}' on Wallhaven.")

            image_info = data["data"][0]
            image_url = image_info["path"]

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Wallhaven: {e}")
        except KeyError:
            raise RuntimeError("❌ Unexpected Wallhaven API response format.")


class BingProvider(ImageProvider):
    """Image provider for Bing Daily Wallpaper."""

    def __init__(self):
        self.api_url = "https://www.bing.com/HPImageArchive.aspx"
        self.base_url = "https://www.bing.com"

    def get_name(self) -> str:
        return "Bing"

    def get_description(self) -> str:
        return "Bing Daily Wallpapers (last 7 days)"

    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
        """Download image from Bing."""
        idx = self._map_category_to_idx(category)

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
                raise RuntimeError(f"❌ No images found on Bing for '{category}'.")

            image_url_path = data["images"][0]["url"]
            image_url = self.base_url + image_url_path

            image_response = requests.get(image_url, timeout=15)
            image_response.raise_for_status()

            print("✅ Download successful!")
            return image_response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Bing: {e}")
        except KeyError:
            raise RuntimeError("❌ Unexpected Bing API response format.")

    @staticmethod
    def _map_category_to_idx(category: str) -> int:
        cat_lower = category.lower()
        if "yesterday" in cat_lower:
            return 1
        if "today" in cat_lower:
            return 0
        import re
        match = re.search(r'(\d+)', cat_lower)
        if match:
            val = int(match.group(1))
            return min(max(val, 0), 7)
        return 0


class PicsumProvider(ImageProvider):
    """Image provider for Picsum Photos (Lorem Picsum)."""

    def __init__(self):
        self.base_url = "https://picsum.photos"

    def get_name(self) -> str:
        return "Picsum"

    def get_description(self) -> str:
        return "Random placeholder images (resolution based)"

    def download_image(self, category: str, mood: str = "", resolution: str = "1920x1080") -> bytes:
        """Download image from Picsum."""
        try:
            width, height = resolution.split('x')
        except ValueError:
            width, height = "1920", "1080"

        if category and category.lower() != "random":
             url = f"{self.base_url}/seed/{category}/{width}/{height}"
        else:
             url = f"{self.base_url}/{width}/{height}"

        if mood == "grayscale":
            url += "?grayscale"
        elif mood == "blur":
            url += "?blur"

        try:
            print(f"⏳ Downloading from Picsum ({url})...")
            response = requests.get(url, allow_redirects=True, timeout=15)
            response.raise_for_status()

            print("✅ Download successful!")
            return response.content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download from Picsum: {e}")
