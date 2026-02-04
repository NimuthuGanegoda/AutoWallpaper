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
from abc import ABC, abstractmethod
import requests
import re
import random
import math
import concurrent.futures
import xml.etree.ElementTree as ET


class ImageProvider(ABC):
    """Abstract base class for image providers."""

    def __init__(self):
        self.session = requests.Session()
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the provider's display name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a brief description of the provider."""
        pass
    
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
        pass

    def set_resolution(self, resolution: str):
        """
        Set the target resolution for the image.
        Optional method for providers that support it.

        Args:
            resolution: Resolution string (e.g., '1920x1080')
        """
        pass

    def _fetch_json(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """
        Helper to fetch JSON data from an API.

        Args:
            url: API endpoint URL
            params: Query parameters
            headers: Request headers

        Returns:
            dict: Parsed JSON data

        Raises:
            RuntimeError: If request fails or response is not JSON
        """
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Connection error ({self.get_name()}): {e}")
        except ValueError:
            raise RuntimeError(f"❌ Invalid JSON response from {self.get_name()}")

    def _download_bytes(self, url: str) -> bytes:
        """
        Helper to download image data as bytes.

        Args:
            url: Image URL

        Returns:
            bytes: Image file content

        Raises:
            RuntimeError: If download fails
        """
        try:
            print(f"⏳ Downloading image from {self.get_name()}...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            print("✅ Download successful!")
            return response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download image: {e}")


class PexelsProvider(ImageProvider):
    """Image provider for Pexels API."""
    
    def __init__(self):
        super().__init__()
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
        else:
             raise RuntimeError(
                "❌ PEXELS_API_KEY not set.\n"
                "Get a free API key from: https://www.pexels.com/api/\n"
                "Then run: export PEXELS_API_KEY='your-key-here'\n"
                "\nAlternatively, use waifu.im (option 3) which requires no API key!"
            )
        
        # Randomize page to ensure variety in loops
        page = random.randint(1, 10)
        params = {"query": query, "per_page": 1, "page": page}
        
        print(f"⏳ Downloading from Pexels ({query}, page {page})...")
        data = self._fetch_json(self.api_url, params=params, headers=headers)

        if not data.get("photos"):
            # Fallback to page 1
            if page != 1:
                print("   No results on random page, trying page 1...")
                params["page"] = 1
                data = self._fetch_json(self.api_url, params=params, headers=headers)

            if not data.get("photos"):
                raise RuntimeError(f"❌ No images found for '{query}' on Pexels.")

        try:
            photo = data["photos"][0]
            image_url = photo["src"].get("original") or photo["src"].get("large")
        except (KeyError, IndexError):
             raise RuntimeError("❌ Unexpected Pexels API response format.")
        
        return self._download_bytes(image_url)


class PixabayProvider(ImageProvider):
    """Image provider for Pixabay API."""
    
    def __init__(self):
        super().__init__()
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
        
        # Randomize page to ensure variety in loops
        page = random.randint(1, 10)
        params = {
            "key": self.api_key,
            "q": query,
            "per_page": 3,
            "page": page,
            "image_type": "photo",
        }
        
        print(f"⏳ Downloading from Pixabay ({query}, page {page})...")
        data = self._fetch_json(self.api_url, params=params)

        if not data.get("hits"):
            # Fallback to page 1
            if page != 1:
                print("   No results on random page, trying page 1...")
                params["page"] = 1
                data = self._fetch_json(self.api_url, params=params)

            if not data.get("hits"):
                raise RuntimeError(f"❌ No images found for '{query}' on Pixabay.")

        try:
            image_data = random.choice(data["hits"])
            image_url = image_data.get("largeImageURL") or image_data.get("webformatURL")
        except (KeyError, IndexError):
             raise RuntimeError("❌ Unexpected Pixabay API response format.")
        
        return self._download_bytes(image_url)


class WaifuImProvider(ImageProvider):
    """Image provider for waifu.im API (anime/waifu images)."""
    
    def __init__(self):
        super().__init__()
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
        
        print(f"⏳ Downloading from waifu.im ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        if not data.get("images"):
            raise RuntimeError(f"❌ No images found for '{category}' on waifu.im.")

        try:
            image_url = data["images"][0]["url"]
        except (KeyError, IndexError):
             raise RuntimeError("❌ Unexpected waifu.im API response format.")
        
        return self._download_bytes(image_url)
    
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
        
        for key in tag_map:
            if key in category_lower:
                return tag_map[key]
        
        return ["waifu"]


class CatgirlProvider(ImageProvider):
    """Image provider for nekos.moe API (catgirl images)."""
    
    def __init__(self):
        super().__init__()
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
        
        print(f"⏳ Downloading from nekos.moe ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        if not data.get("images"):
            raise RuntimeError(f"❌ No catgirl images found for '{category}' on nekos.moe.")

        try:
            image_id = data["images"][0]["id"]
            image_url = f"https://nekos.moe/image/{image_id}"
        except (KeyError, IndexError):
             raise RuntimeError("❌ Unexpected nekos.moe API response format.")
        
        return self._download_bytes(image_url)
    
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
        super().__init__()
        self.api_url = "https://api.unsplash.com/photos/random"
        self.api_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
        self.orientation = "landscape"

    def get_name(self) -> str:
        return "Unsplash"

    def get_description(self) -> str:
        return "Professional photos (requires Access Key, 50 req/hour)"

    def set_resolution(self, resolution: str):
        try:
            if "x" in resolution:
                parts = resolution.lower().split("x")
                if len(parts) >= 2:
                    width, height = int(parts[0]), int(parts[1])
                    if width > height:
                        self.orientation = "landscape"
                    elif height > width:
                        self.orientation = "portrait"
                    else:
                        self.orientation = "squarish"
        except ValueError:
            pass

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

        params = {"orientation": self.orientation, "client_id": self.api_key}
        if query and query.lower() != "random":
             params["query"] = query

        print(f"⏳ Downloading from Unsplash ({query})...")
        data = self._fetch_json(self.api_url, params=params)

        if isinstance(data, list):
            data = data[0]

        try:
            image_url = data["urls"]["raw"]
        except (KeyError, IndexError):
            raise RuntimeError("❌ Unexpected Unsplash API response format.")

        return self._download_bytes(image_url)


class WallhavenProvider(ImageProvider):
    """Image provider for Wallhaven API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://wallhaven.cc/api/v1/search"
        self.api_key = os.getenv("WALLHAVEN_API_KEY", "")
        self.ratios = ""

    def get_name(self) -> str:
        return "Wallhaven"

    def get_description(self) -> str:
        return "Anime & General wallpapers (API key optional)"

    def set_resolution(self, resolution: str):
        try:
            if "x" in resolution:
                parts = resolution.lower().split("x")
                if len(parts) >= 2:
                    width, height = int(parts[0]), int(parts[1])
                    gcd_val = math.gcd(width, height)
                    w_ratio = width // gcd_val
                    h_ratio = height // gcd_val
                    self.ratios = f"{w_ratio}x{h_ratio}"
        except ValueError:
            pass

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = category
        if mood:
            query = f"{category} {mood}"

        params = {
            "q": query,
            "sorting": "random",
            "purity": "100", # SFW
        }
        if self.ratios:
            params["ratios"] = self.ratios

        if self.api_key:
            params["apikey"] = self.api_key

        print(f"⏳ Downloading from Wallhaven ({query})...")
        # Wallhaven requires a user agent or sometimes blocks
        headers = {"User-Agent": "EasyWallpaper/1.0"}
        data = self._fetch_json(self.api_url, params=params, headers=headers)

        if not data.get("data"):
             raise RuntimeError(f"❌ No images found for '{query}' on Wallhaven.")

        try:
            image_url = data["data"][0]["path"]
        except (KeyError, IndexError):
            raise RuntimeError("❌ Unexpected Wallhaven API response format.")

        return self._download_bytes(image_url)


class BingProvider(ImageProvider):
    """Image provider for Bing Daily Wallpaper."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://www.bing.com/HPImageArchive.aspx"

    def get_name(self) -> str:
        return "Bing"

    def get_description(self) -> str:
        return "Bing Daily Wallpaper (Today, Yesterday, etc.)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Map category to idx
        idx = 0
        cat_lower = category.lower()

        if "random" in cat_lower:
            idx = random.randint(0, 7)
        elif "yesterday" in cat_lower:
            idx = 1
        elif "days ago" in cat_lower:
            try:
                match = re.search(r"(\d+)", cat_lower)
                if match:
                    idx = int(match.group(1))
            except Exception:
                idx = 0

        if idx > 7: idx = 7

        params = {
            "format": "js",
            "idx": idx,
            "n": 1,
            "mkt": "en-US"
        }

        print(f"⏳ Downloading from Bing ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        if not data.get("images"):
             raise RuntimeError("❌ Failed to get Bing image info.")

        try:
            url_base = data["images"][0]["url"]
            image_url = f"https://www.bing.com{url_base}"
        except (KeyError, IndexError):
             raise RuntimeError("❌ Unexpected Bing API response format.")

        return self._download_bytes(image_url)


class PicsumProvider(ImageProvider):
    """Image provider for Lorem Picsum."""

    def __init__(self):
        super().__init__()
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

        # Picsum is different, it returns image directly on the URL
        return self._download_bytes(url)


class NasaApodProvider(ImageProvider):
    """Image provider for NASA Astronomy Picture of the Day."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.nasa.gov/planetary/apod"
        self.api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")

    def get_name(self) -> str:
        return "NASA APOD"

    def get_description(self) -> str:
        return "Astronomy Picture of the Day (Space images)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        params = {"api_key": self.api_key}

        if category.lower() == "random":
            params["count"] = 1

        print(f"⏳ Downloading from NASA APOD ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        # Handle list response (random) vs dict response (today)
        if isinstance(data, list):
            if not data:
                raise RuntimeError("❌ No images returned from NASA API.")
            image_data = data[0]
        else:
            image_data = data

        image_url = image_data.get("hdurl") or image_data.get("url")
        if not image_url:
                raise RuntimeError("❌ No image URL found in NASA response.")

        return self._download_bytes(image_url)


class TheCatApiProvider(ImageProvider):
    """Image provider for TheCatAPI."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.thecatapi.com/v1/images/search"

    def get_name(self) -> str:
        return "TheCatAPI"

    def get_description(self) -> str:
        return "Random cat images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Downloading from TheCatAPI...")
        data = self._fetch_json(self.api_url, params={"limit": 1})

        if not data:
            raise RuntimeError("❌ No images returned from TheCatAPI.")

        try:
            image_url = data[0]["url"]
        except (KeyError, IndexError):
            raise RuntimeError("❌ Unexpected TheCatAPI response format.")

        return self._download_bytes(image_url)


class TheDogApiProvider(ImageProvider):
    """Image provider for TheDogAPI."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.thedogapi.com/v1/images/search"

    def get_name(self) -> str:
        return "TheDogAPI"

    def get_description(self) -> str:
        return "Random dog images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Downloading from TheDogAPI...")
        data = self._fetch_json(self.api_url, params={"limit": 1})

        if not data:
            raise RuntimeError("❌ No images returned from TheDogAPI.")

        try:
            image_url = data[0]["url"]
        except (KeyError, IndexError):
            raise RuntimeError("❌ Unexpected TheDogAPI response format.")

        return self._download_bytes(image_url)


class MetMuseumProvider(ImageProvider):
    """Image provider for The Metropolitan Museum of Art."""

    def __init__(self):
        super().__init__()
        self.search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
        self.object_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"

    def get_name(self) -> str:
        return "The Met"

    def get_description(self) -> str:
        return "Classic art from The Metropolitan Museum of Art"

    def _check_object(self, object_id):
        """Helper to check a single object ID."""
        try:
            url = f"{self.object_url}/{object_id}"
            # Use session directly to handle 404s gracefully without exception overhead
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return None

            obj_data = resp.json()
            image_url = obj_data.get("primaryImage")
            if image_url:
                return (image_url, obj_data.get('title', 'Unknown'))
        except Exception:
            pass
        return None

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = category if category.lower() != "random" else "painting"

        print(f"⏳ Searching The Met ({query})...")
        data = self._fetch_json(self.search_url, params={"q": query, "hasImages": "true"})

        object_ids = data.get("objectIDs", [])
        if not object_ids:
            raise RuntimeError(f"❌ No objects found for '{query}' at The Met.")

        # Select up to 10 random IDs to check in parallel
        num_checks = min(len(object_ids), 10)
        selected_ids = random.sample(object_ids, num_checks)

        print(f"⏳ Checking {num_checks} objects for valid images...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self._check_object, oid) for oid in selected_ids]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    image_url, title = result
                    print(f"⏳ Found art: {title}...")
                    # Cancel other futures (best effort)
                    for f in futures: f.cancel()
                    return self._download_bytes(image_url)

        raise RuntimeError("❌ Failed to find a valid image after parallel checks.")


class WikimediaCommonsProvider(ImageProvider):
    """Image provider for Wikimedia Commons."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://commons.wikimedia.org/w/api.php"
        # Set User-Agent for all requests (API and image download)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def get_name(self) -> str:
        return "Wikimedia Commons"

    def get_description(self) -> str:
        return "Massive media repository (Creative Commons)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = category
        if mood:
            query = f"{category} {mood}"

        # Search for images in 'File' namespace (6)
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,  # File namespace
            "gsrlimit": 20,     # Fetch 20 results
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }

        print(f"⏳ Searching Wikimedia Commons ({query})...")
        data = self._fetch_json(self.api_url, params=params)

        pages = data.get("query", {}).get("pages", {})
        if not pages:
             raise RuntimeError(f"❌ No images found for '{query}' on Wikimedia Commons.")

        # Filter pages that have imageinfo and url, and are valid image types
        valid_pages = []
        valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
        for page in pages.values():
            if "imageinfo" in page and page["imageinfo"]:
                image_info = page["imageinfo"][0]
                if "url" in image_info:
                    url = image_info["url"]
                    if url.lower().endswith(valid_extensions):
                        valid_pages.append(page)

        if not valid_pages:
             raise RuntimeError(f"❌ No valid images (jpg/png/webp) found for '{query}'.")

        # Pick a random one
        chosen = random.choice(valid_pages)
        image_url = chosen["imageinfo"][0]["url"]
        title = chosen.get("title", "Unknown")
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)


class CountryFlagsProvider(ImageProvider):
    """Image provider for Country Flags (FlagCDN)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://flagcdn.com/w2560"
        self.codes = [
            "us", "gb", "ca", "au", "jp", "de", "fr", "it", "es", "br",
            "in", "cn", "ru", "za", "kr", "mx", "id", "tr", "sa", "ar"
        ]

    def get_name(self) -> str:
        return "Country Flags"

    def get_description(self) -> str:
        return "High quality country flags"

    def download_image(self, category: str, mood: str = "") -> bytes:
        code = category.lower()
        if code == "random":
            code = random.choice(self.codes)

        # Simple mapping for common names if user types "usa" instead of "us"
        mapping = {"usa": "us", "uk": "gb", "japan": "jp", "germany": "de", "france": "fr"}
        code = mapping.get(code, code)

        url = f"{self.base_url}/{code}.png"
        print(f"⏳ Downloading flag for '{code}'...")

        # FlagCDN returns 404 for invalid codes.
        try:
             # We can't use _fetch_json because it's an image.
             # _download_bytes handles the get.
             # But if it fails, we want a nice message.
             # _download_bytes raises RuntimeError on failure.
             return self._download_bytes(url)
        except RuntimeError:
             raise RuntimeError(f"❌ Flag not found for code '{code}'. Try 2-letter ISO code.")


class AmiiboApiProvider(ImageProvider):
    """Image provider for Nintendo Amiibo."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://www.amiiboapi.com/api/amiibo/"

    def get_name(self) -> str:
        return "Amiibo API"

    def get_description(self) -> str:
        return "Nintendo Amiibo Figures"

    def download_image(self, category: str, mood: str = "") -> bytes:
        params = {}
        if category and category.lower() != "random":
             params["name"] = category

        print(f"⏳ Fetching Amiibo ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        amiibo_list = data.get("amiibo", [])
        if not amiibo_list:
             # Try character search if name search failed?
             # The API has "name", "character", "gameSeries", etc.
             # "name" is usually the figure name.
             raise RuntimeError(f"❌ No Amiibo found for '{category}'.")

        # Pick random if multiple
        chosen = random.choice(amiibo_list)
        image_url = chosen.get("image")
        name = chosen.get("name", "Unknown")
        series = chosen.get("gameSeries", "")

        print(f"   Selected: {name} ({series})")

        if not image_url:
            raise RuntimeError("❌ No image URL found.")

        return self._download_bytes(image_url)


class CoinCapProvider(ImageProvider):
    """Image provider for Crypto Logos (CoinCap)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://assets.coincap.io/assets/icons"
        self.common_coins = [
            "BTC", "ETH", "USDT", "BNB", "XRP", "USDC", "SOL", "ADA", "DOGE", "TRX"
        ]

    def get_name(self) -> str:
        return "CoinCap (Crypto)"

    def get_description(self) -> str:
        return "Cryptocurrency Logos"

    def download_image(self, category: str, mood: str = "") -> bytes:
        symbol = category.upper()
        if category.lower() == "random":
             symbol = random.choice(self.common_coins)

        url = f"{self.base_url}/{symbol.lower()}@2x.png"
        print(f"⏳ Downloading logo for '{symbol}'...")

        try:
             return self._download_bytes(url)
        except RuntimeError:
             raise RuntimeError(f"❌ Logo not found for '{symbol}'.")


class DiceBearProvider(ImageProvider):
    """Image provider for DiceBear Avatars."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.dicebear.com/7.x"
        self.styles = [
            "adventurer", "avataaars", "bottts", "fun-emoji", "lorelei",
            "notionists", "pixel-art", "thumbs"
        ]

    def get_name(self) -> str:
        return "DiceBear Avatars"

    def get_description(self) -> str:
        return "Generated Avatars (DiceBear)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Category can be style
        style = category.lower()
        seed = str(random.randint(0, 999999))

        if style == "random" or style not in self.styles:
            if style != "random":
                seed = style # Use category as seed if it's not a known style
            style = random.choice(self.styles)

        url = f"{self.base_url}/{style}/png?seed={seed}&size=1024"
        print(f"⏳ Generating avatar ({style}, seed={seed})...")

        return self._download_bytes(url)


class LoremFlickrProvider(ImageProvider):
    """Image provider for Lorem Flickr."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://loremflickr.com"
        self.width = 1920
        self.height = 1080

    def get_name(self) -> str:
        return "Lorem Flickr"

    def get_description(self) -> str:
        return "Random photos by keyword (Simple & Fast)"

    def set_resolution(self, resolution: str):
        try:
            if "x" in resolution:
                parts = resolution.lower().split("x")
                if len(parts) >= 2:
                    self.width = int(parts[0])
                    self.height = int(parts[1])
        except ValueError:
            pass

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Construct URL: https://loremflickr.com/{width}/{height}/{keywords}
        keywords = category
        if mood:
            keywords = f"{category},{mood}"

        # Replace spaces with commas or let URL encoding handle it?
        # LoremFlickr uses commas for multiple keywords
        keywords = keywords.replace(" ", ",")

        url = f"{self.base_url}/{self.width}/{self.height}/{keywords}"

        # Note: LoremFlickr redirects to the actual image.
        # requests.get follows redirects by default.
        return self._download_bytes(url)


class RedditProvider(ImageProvider):
    """Image provider for Reddit."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.reddit.com/r"
        # Reddit requires a custom User-Agent to avoid blocking
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def get_name(self) -> str:
        return "Reddit"

    def get_description(self) -> str:
        return "Images from subreddits (Hot, Top, New)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        subreddit = category
        sort = mood if mood else "hot"

        # Construct URL: https://www.reddit.com/r/{subreddit}/{sort}.json
        url = f"{self.base_url}/{subreddit}/{sort}.json"

        print(f"⏳ Fetching from r/{subreddit} ({sort})...")

        # Limit to 100 posts to find valid images
        params = {"limit": 100}

        try:
            data = self._fetch_json(url, params=params)
        except RuntimeError as e:
            if "403" in str(e) or "429" in str(e):
                raise RuntimeError("❌ Reddit API blocked the request (Rate limit or IP block). Try again later.")
            raise e

        posts = data.get("data", {}).get("children", [])
        if not posts:
            raise RuntimeError(f"❌ No posts found in r/{subreddit}.")

        valid_images = []
        valid_extensions = (".jpg", ".jpeg", ".png", ".webp")

        for post in posts:
            post_data = post.get("data", {})
            url = post_data.get("url", "")

            # Check for direct image links
            if url.lower().endswith(valid_extensions):
                valid_images.append(url)
            # Sometimes reddit hosts images but URL doesn't end in extension?
            # Usually 'url_overridden_by_dest' works too.

        if not valid_images:
            raise RuntimeError(f"❌ No valid images found in r/{subreddit} current feed.")

        image_url = random.choice(valid_images)
        return self._download_bytes(image_url)


class DeviantArtProvider(ImageProvider):
    """Image provider for DeviantArt RSS."""

    def __init__(self):
        super().__init__()
        self.rss_url = "https://backend.deviantart.com/rss.xml"

    def get_name(self) -> str:
        return "DeviantArt"

    def get_description(self) -> str:
        return "Popular art via RSS (No API key needed)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = f"boost:popular {category}"
        if mood:
            query = f"{query} {mood}"

        params = {"q": query}

        print(f"⏳ Searching DeviantArt ({query})...")

        # We need raw XML, not JSON
        try:
            response = self.session.get(self.rss_url, params=params, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Connection error (DeviantArt): {e}")

        # Parse XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            raise RuntimeError("❌ Failed to parse DeviantArt RSS feed.")

        # Find all items
        items = root.findall(".//item")
        if not items:
            raise RuntimeError(f"❌ No results found for '{category}' on DeviantArt.")

        # Namespaces in RSS are tricky with ElementTree.
        # media:content is usually what we want.
        # However, finding by tag name without namespace map is hard if not defined.
        # Let's iterate and look for media:content or use simple finding.

        valid_urls = []

        # Namespace map
        namespaces = {
            'media': 'http://search.yahoo.com/mrss/'
        }

        for item in items:
            # Try to find media:content
            media = item.find('media:content', namespaces)
            if media is not None:
                url = media.get('url')
                if url:
                    valid_urls.append(url)
            else:
                # Fallback to parsing description for img tag?
                # Or parsing <media:content> manually if namespace fails
                pass

        if not valid_urls:
             # Try a simpler approach if namespace failed or no media content found
             # Sometimes 'guid' works? No, that's the page.
             raise RuntimeError(f"❌ No image URLs extracted from DeviantArt RSS.")

        image_url = random.choice(valid_urls)
        return self._download_bytes(image_url)


class KonachanProvider(ImageProvider):
    """Image provider for Konachan.net (Anime wallpapers)."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://konachan.net/post.json"

    def get_name(self) -> str:
        return "Konachan"

    def get_description(self) -> str:
        return "Anime Wallpapers (Konachan.net)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        tags = category
        if mood:
            tags = f"{category} {mood}"

        # If category is "random", we don't send tags to get random latest
        params = {"limit": 100}
        if category.lower() != "random":
            params["tags"] = tags

        print(f"⏳ Searching Konachan ({tags})...")
        data = self._fetch_json(self.api_url, params=params)

        if not data:
             raise RuntimeError(f"❌ No images found for '{tags}' on Konachan.")

        # Filter for Safe images if needed?
        # Let's verify rating. s=safe, q=questionable, e=explicit
        # We prefer safe by default unless user asked for something specific?
        # But we don't have a safety toggle in the UI.
        # We'll filter for safe if the user didn't specify 'nsfw' or similar in tags.

        check_safety = "nsfw" not in tags.lower() and "lewd" not in tags.lower()

        valid_images = []
        for post in data:
            if check_safety and post.get("rating") != "s":
                continue

            # Use file_url (original) or jpeg_url (large)
            url = post.get("file_url") or post.get("jpeg_url")
            if url:
                valid_images.append(url)

        if not valid_images:
            if check_safety:
                 raise RuntimeError(f"❌ No SAFE images found for '{tags}'. Try adding 'safe' to search.")
            raise RuntimeError(f"❌ No images found for '{tags}'.")

        image_url = random.choice(valid_images)

        # Konachan images are often HTTP, but we should handle that.
        if image_url.startswith("//"):
            image_url = "https:" + image_url

        return self._download_bytes(image_url)


class FoodishProvider(ImageProvider):
    """Image provider for Foodish API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://foodish-api.com/api/"

    def get_name(self) -> str:
        return "Foodish"

    def get_description(self) -> str:
        return "Random tasty food images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Foodish has specific endpoints for categories: /images/burger, /images/pizza, etc.
        # But the main API returns random.
        # Or we can use https://foodish-api.com/api/images/{category}
        # Categories: biryani, burger, butter-chicken, dessert, dosa, idli, pasta, pizza, rice, samosa

        valid_categories = [
            "biryani", "burger", "butter-chicken", "dessert", "dosa",
            "idli", "pasta", "pizza", "rice", "samosa"
        ]

        url = self.api_url
        if category.lower() in valid_categories:
            url = f"https://foodish-api.com/api/images/{category.lower()}"

        print(f"⏳ Fetching from Foodish ({category if category.lower() in valid_categories else 'Random'})...")
        data = self._fetch_json(url)

        image_url = data.get("image")
        if not image_url:
            raise RuntimeError("❌ No image returned from Foodish.")

        return self._download_bytes(image_url)

class FoxProvider(ImageProvider):
    """Image provider for Random Fox API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://randomfox.ca/floof/"

    def get_name(self) -> str:
        return "Random Fox"

    def get_description(self) -> str:
        return "Random fox images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Downloading from Random Fox...")
        data = self._fetch_json(self.api_url)

        image_url = data.get("image")
        if not image_url:
            raise RuntimeError("❌ No image returned from Random Fox.")

        return self._download_bytes(image_url)


class MemeProvider(ImageProvider):
    """Image provider for Meme API."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://meme-api.com/gimme"

    def get_name(self) -> str:
        return "Meme API"

    def get_description(self) -> str:
        return "Memes from Reddit"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Category can be a subreddit
        url = self.base_url
        if category and category.lower() != "random":
             url = f"{self.base_url}/{category}"

        print(f"⏳ Fetching meme ({category})...")
        data = self._fetch_json(url)

        if "code" in data:
             # Error response
             message = data.get("message", "Unknown error")
             raise RuntimeError(f"❌ Meme API Error: {message}")

        image_url = data.get("url")
        if not image_url:
            raise RuntimeError("❌ No image URL returned from Meme API.")

        return self._download_bytes(image_url)


class ZenQuotesProvider(ImageProvider):
    """Image provider for ZenQuotes."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://zenquotes.io/api/image"

    def get_name(self) -> str:
        return "ZenQuotes"

    def get_description(self) -> str:
        return "Inspirational quotes on images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # ZenQuotes returns image bytes directly at the URL
        print(f"⏳ Downloading from ZenQuotes...")
        return self._download_bytes(self.api_url)


class SafebooruProvider(ImageProvider):
    """Image provider for Safebooru (Anime)."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://safebooru.org/index.php"

    def get_name(self) -> str:
        return "Safebooru"

    def get_description(self) -> str:
        return "Safe Anime Wallpapers"

    def download_image(self, category: str, mood: str = "") -> bytes:
        tags = category
        if mood:
            tags = f"{category} {mood}"

        # API: page=dapi&s=post&q=index&json=1&limit=100
        params = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": "1",
            "limit": 100
        }

        if category.lower() != "random":
            params["tags"] = tags

        print(f"⏳ Searching Safebooru ({tags})...")
        data = self._fetch_json(self.api_url, params=params)

        if not data:
             raise RuntimeError(f"❌ No images found for '{tags}' on Safebooru.")

        valid_images = []
        for post in data:
            # We prefer file_url or sample_url
            if "file_url" in post:
                valid_images.append(post["file_url"])
            elif "image" in post and "directory" in post:
                 # Fallback construction if file_url is missing
                 # https://safebooru.org/images/{directory}/{image}
                 url = f"https://safebooru.org/images/{post['directory']}/{post['image']}"
                 valid_images.append(url)

        if not valid_images:
            raise RuntimeError(f"❌ No valid images found for '{tags}'.")

        image_url = random.choice(valid_images)
        return self._download_bytes(image_url)


class XKCDProvider(ImageProvider):
    """Image provider for XKCD."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://xkcd.com/info.0.json"

    def get_name(self) -> str:
        return "XKCD"

    def get_description(self) -> str:
        return "XKCD Webcomics"

    def download_image(self, category: str, mood: str = "") -> bytes:
        url = self.api_url

        # If random, first get current to find max num, then pick random
        if category.lower() == "random":
             try:
                 current = self._fetch_json(self.api_url)
                 max_num = current["num"]
                 rand_num = random.randint(1, max_num)
                 url = f"https://xkcd.com/{rand_num}/info.0.json"
             except Exception as e:
                 print(f"⚠️ Failed to get random XKCD, defaulting to current: {e}")
                 url = self.api_url

        print(f"⏳ Fetching XKCD ({category})...")
        data = self._fetch_json(url)

        image_url = data.get("img")
        if not image_url:
            raise RuntimeError("❌ No image URL returned from XKCD.")

        return self._download_bytes(image_url)


class DogCeoProvider(ImageProvider):
    """Image provider for Dog CEO."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://dog.ceo/api/breeds/image/random"

    def get_name(self) -> str:
        return "Dog CEO"

    def get_description(self) -> str:
        return "Random Dog Images (Dog CEO)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Fetching from Dog CEO...")
        data = self._fetch_json(self.api_url)

        image_url = data.get("message")
        if not image_url:
            raise RuntimeError("❌ No image URL returned from Dog CEO.")

        return self._download_bytes(image_url)


class ImgFlipProvider(ImageProvider):
    """Image provider for ImgFlip Memes."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.imgflip.com/get_memes"

    def get_name(self) -> str:
        return "ImgFlip"

    def get_description(self) -> str:
        return "Popular Meme Templates"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Fetching from ImgFlip...")
        data = self._fetch_json(self.api_url)

        if not data.get("success"):
            raise RuntimeError("❌ ImgFlip API returned failure.")

        memes = data.get("data", {}).get("memes", [])
        if not memes:
            raise RuntimeError("❌ No memes found from ImgFlip.")

        # Pick a random meme from top 100
        meme = random.choice(memes)
        image_url = meme.get("url")

        if not image_url:
            raise RuntimeError("❌ No image URL in ImgFlip meme.")

        return self._download_bytes(image_url)


class CoffeeProvider(ImageProvider):
    """Image provider for Coffee API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://coffee.alexflipnote.dev/random.json"

    def get_name(self) -> str:
        return "Coffee"

    def get_description(self) -> str:
        return "Random Coffee Images"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Fetching coffee...")
        data = self._fetch_json(self.api_url)

        image_url = data.get("file")
        if not image_url:
            raise RuntimeError("❌ No image URL returned from Coffee API.")

        return self._download_bytes(image_url)


class CataasProvider(ImageProvider):
    """Image provider for Cataas (Cat as a service)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://cataas.com"

    def get_name(self) -> str:
        return "Cataas"

    def get_description(self) -> str:
        return "Cat as a Service (Cataas)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # We use ?json=true to get the URL
        url = f"{self.base_url}/cat?json=true"

        # We can also add tags if category is not "random"
        # https://cataas.com/cat/{tag}?json=true
        if category and category.lower() != "random":
             url = f"{self.base_url}/cat/{category}?json=true"

        print(f"⏳ Fetching from Cataas ({category})...")
        data = self._fetch_json(url)

        # Response: {"id": "...", "url": "..."}
        # Note: The "url" field in response might be relative, e.g. "/cat/..."

        rel_url = data.get("url")
        if not rel_url:
             # Sometimes it might just return the id?
             # Let's rely on 'id' if 'url' is missing
             _id = data.get("_id") # Sometimes it's _id
             if not _id:
                 _id = data.get("id")

             if _id:
                 rel_url = f"/cat/{_id}"
             else:
                 raise RuntimeError("❌ No URL or ID returned from Cataas.")

        if not rel_url.startswith("http"):
            image_url = f"{self.base_url}{rel_url}"
        else:
            image_url = rel_url

        return self._download_bytes(image_url)


class PlaceBearProvider(ImageProvider):
    """Image provider for PlaceBear."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://placebear.com"
        self.width = 1920
        self.height = 1080

    def get_name(self) -> str:
        return "PlaceBear"

    def get_description(self) -> str:
        return "Bear placeholder images"

    def set_resolution(self, resolution: str):
        try:
            if "x" in resolution:
                parts = resolution.lower().split("x")
                if len(parts) >= 2:
                    self.width = int(parts[0])
                    self.height = int(parts[1])
        except ValueError:
            pass

    def download_image(self, category: str, mood: str = "") -> bytes:
        url = f"{self.base_url}/{self.width}/{self.height}"
        print(f"⏳ Downloading from PlaceBear...")
        return self._download_bytes(url)


class PlaceDogProvider(ImageProvider):
    """Image provider for PlaceDog."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://placedog.net"
        self.width = 1920
        self.height = 1080

    def get_name(self) -> str:
        return "PlaceDog"

    def get_description(self) -> str:
        return "Dog placeholder images"

    def set_resolution(self, resolution: str):
        try:
            if "x" in resolution:
                parts = resolution.lower().split("x")
                if len(parts) >= 2:
                    self.width = int(parts[0])
                    self.height = int(parts[1])
        except ValueError:
            pass

    def download_image(self, category: str, mood: str = "") -> bytes:
        # https://placedog.net/1920/1080?random
        url = f"{self.base_url}/{self.width}/{self.height}?random"
        print(f"⏳ Downloading from PlaceDog...")
        return self._download_bytes(url)


class RobohashProvider(ImageProvider):
    """Image provider for Robohash."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://robohash.org"

    def get_name(self) -> str:
        return "Robohash"

    def get_description(self) -> str:
        return "Generated robots/monsters/cats"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # category can be used as the seed text
        text = category if category.lower() != "random" else str(random.random())

        # Set can be controlled by mood or we can map it?
        # Sets: set1 (robots), set2 (monsters), set3 (disembodied heads), set4 (cats)
        # Let's map "monster" -> set2, "cat" -> set4, default -> set1

        set_val = "set1"
        if "monster" in category.lower() or "monster" in mood.lower():
            set_val = "set2"
        elif "cat" in category.lower() or "cat" in mood.lower():
            set_val = "set4"

        url = f"{self.base_url}/{text}.png?set={set_val}&size=1024x1024"

        print(f"⏳ Downloading from Robohash ({set_val})...")
        return self._download_bytes(url)


class InspirobotProvider(ImageProvider):
    """Image provider for Inspirobot (AI Generated Quotes)."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://inspirobot.me/api?generate=true"

    def get_name(self) -> str:
        return "Inspirobot"

    def get_description(self) -> str:
        return "AI generated inspirational quotes"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Generating quote from Inspirobot...")
        # Inspirobot returns the URL in the response body text
        try:
            response = self.session.get(self.api_url, timeout=15)
            response.raise_for_status()
            image_url = response.text
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Connection error (Inspirobot): {e}")

        return self._download_bytes(image_url)


class JikanProvider(ImageProvider):
    """Image provider for Jikan (MyAnimeList)."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.jikan.moe/v4/random/anime"

    def get_name(self) -> str:
        return "Jikan (Anime)"

    def get_description(self) -> str:
        return "Random Anime Info & Art (MyAnimeList)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Fetching random anime from Jikan...")

        url = self.api_url
        params = {}

        if category and category.lower() != "random":
             # Use search
             url = "https://api.jikan.moe/v4/anime"
             params = {"q": category, "limit": 1}
             print(f"⏳ Searching Jikan for '{category}'...")

        # Jikan has strict rate limits, so we handle it gracefully
        try:
             data = self._fetch_json(url, params=params)
        except RuntimeError as e:
             if "429" in str(e):
                 raise RuntimeError("❌ Jikan API Rate Limit Reached. Please wait a moment.")
             raise e

        anime = None
        if category and category.lower() != "random":
            if not data.get("data"):
                 raise RuntimeError(f"❌ No anime found for '{category}'.")
            anime = data["data"][0]
        else:
            anime = data.get("data")
            if not anime:
                 raise RuntimeError("❌ No data returned from Jikan.")

        images = anime.get("images", {}).get("jpg", {})
        image_url = images.get("large_image_url") or images.get("image_url")

        if not image_url:
             raise RuntimeError("❌ No image URL found.")

        title = anime.get("title_english") or anime.get("title")
        print(f"   Found: {title}")

        return self._download_bytes(image_url)


class ScryfallProvider(ImageProvider):
    """Image provider for Scryfall (Magic: The Gathering)."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.scryfall.com/cards/random"

    def get_name(self) -> str:
        return "Scryfall"

    def get_description(self) -> str:
        return "Magic: The Gathering Card Art"

    def download_image(self, category: str, mood: str = "") -> bytes:
        params = {}
        if category and category.lower() != "random":
             params["q"] = f"art:{category}" # Search for art tags? or type?
             # 'art:city' finds cards with city in art.
             # 't:dragon' finds dragons.
             # Let's try to be smart. If mood is set, use it?
             # If category is a creature type, use t:.
             # Let's just use 'q' parameter which searches everything.
             params["q"] = category

        print(f"⏳ Fetching from Scryfall ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        image_uris = data.get("image_uris")
        if not image_uris:
            # Sometimes double-faced cards have 'card_faces'
            card_faces = data.get("card_faces")
            if card_faces and "image_uris" in card_faces[0]:
                image_uris = card_faces[0]["image_uris"]
            else:
                raise RuntimeError("❌ No image URIs found on Scryfall card.")

        # Prefer art_crop (just the art) or large (full card)
        # For wallpapers, art_crop is usually better?
        # But text is cool too. Let's use large (full card) or border_crop.
        # User might want the art. Let's defaults to art_crop if available, else large.
        image_url = image_uris.get("art_crop") or image_uris.get("large")

        return self._download_bytes(image_url)


class HTTPCatsProvider(ImageProvider):
    """Image provider for HTTP Cats."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://http.cat"
        self.codes = [
            100, 101, 102, 103,
            200, 201, 202, 203, 204, 205, 206, 207,
            300, 301, 302, 303, 304, 305, 307, 308,
            400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422, 423, 424, 425, 426, 429, 431, 444, 450, 451, 497, 498, 499,
            500, 501, 502, 503, 504, 506, 507, 508, 509, 510, 511, 521, 522, 523, 525, 599
        ]

    def get_name(self) -> str:
        return "HTTP Cats"

    def get_description(self) -> str:
        return "Cats for every HTTP Status Code"

    def download_image(self, category: str, mood: str = "") -> bytes:
        code = 404
        if category.isdigit():
            code = int(category)
        elif category.lower() == "random":
            code = random.choice(self.codes)

        url = f"{self.base_url}/{code}"
        print(f"⏳ Downloading HTTP Cat {code}...")
        return self._download_bytes(url)


class ArtInstituteProvider(ImageProvider):
    """Image provider for Art Institute of Chicago."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.artic.edu/api/v1/artworks"

    def get_name(self) -> str:
        return "Art Institute Chicago"

    def get_description(self) -> str:
        return "Classic artworks from Chicago"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Docs: https://api.artic.edu/docs/#collections-1
        # Search: /search?q={query}&fields=id,title,image_id

        url = f"{self.api_url}/search"
        params = {
            "q": category if category.lower() != "random" else "painting",
            "fields": "id,title,image_id",
            "limit": 20
        }

        print(f"⏳ Searching Art Institute ({params['q']})...")
        data = self._fetch_json(url, params=params)

        items = data.get("data", [])
        if not items:
            raise RuntimeError(f"❌ No artworks found for '{category}'.")

        # Filter items with image_id
        valid_items = [item for item in items if item.get("image_id")]
        if not valid_items:
            raise RuntimeError(f"❌ No valid images found for '{category}'.")

        chosen = random.choice(valid_items)
        image_id = chosen.get("image_id")
        title = chosen.get("title", "Unknown")

        # Get IIIF URL from config if available, else hardcode default
        # The response usually has a 'config' key but it's at the root.
        iiif_url = data.get("config", {}).get("iiif_url", "https://www.artic.edu/iiif/2")

        # Construct full URL
        # {iiif_url}/{identifier}/full/843,/0/default.jpg
        image_url = f"{iiif_url}/{image_id}/full/1600,/0/default.jpg"

        print(f"   Selected: {title}")
        return self._download_bytes(image_url)


class RickAndMortyProvider(ImageProvider):
    """Image provider for Rick and Morty API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://rickandmortyapi.com/api/character"

    def get_name(self) -> str:
        return "Rick and Morty"

    def get_description(self) -> str:
        return "Characters from Rick and Morty"

    def download_image(self, category: str, mood: str = "") -> bytes:
        if category.lower() == "random":
            # Get random ID. Max is around 826.
            # But let's fetch a random page to be safe if ID gap exists?
            # Or just use the documented ID range.
            rand_id = random.randint(1, 826)
            url = f"{self.api_url}/{rand_id}"
            print(f"⏳ Fetching random character (ID: {rand_id})...")
            data = self._fetch_json(url)

        else:
            # Search by name
            params = {"name": category}
            print(f"⏳ Searching Rick and Morty for '{category}'...")
            data = self._fetch_json(self.api_url, params=params)

            results = data.get("results", [])
            if not results:
                raise RuntimeError(f"❌ No characters found for '{category}'.")

            data = random.choice(results)

        image_url = data.get("image")
        name = data.get("name", "Unknown")
        print(f"   Selected: {name}")

        if not image_url:
            raise RuntimeError("❌ No image URL found.")

        return self._download_bytes(image_url)


class OpenLibraryProvider(ImageProvider):
    """Image provider for Open Library (Book Covers)."""

    def __init__(self):
        super().__init__()
        self.search_url = "https://openlibrary.org/search.json"
        self.cover_url = "https://covers.openlibrary.org/b/id"

    def get_name(self) -> str:
        return "Open Library"

    def get_description(self) -> str:
        return "Book Covers"

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = category if category.lower() != "random" else "tolkien"

        print(f"⏳ Searching Open Library for books ({query})...")
        params = {"q": query, "limit": 20}

        data = self._fetch_json(self.search_url, params=params)
        docs = data.get("docs", [])

        if not docs:
            raise RuntimeError(f"❌ No books found for '{query}'.")

        # Filter for cover_i
        valid_docs = [doc for doc in docs if doc.get("cover_i")]
        if not valid_docs:
            raise RuntimeError(f"❌ No books with covers found for '{query}'.")

        chosen = random.choice(valid_docs)
        cover_id = chosen.get("cover_i")
        title = chosen.get("title", "Unknown")

        image_url = f"{self.cover_url}/{cover_id}-L.jpg"
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)


class TheMealDbProvider(ImageProvider):
    """Image provider for TheMealDB."""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("THEMEALDB_API_KEY", "1")
        self.api_url = f"https://www.themealdb.com/api/json/v1/{self.api_key}/"

    def get_name(self) -> str:
        return "TheMealDB"

    def get_description(self) -> str:
        return "Random Meals and Recipes"

    def download_image(self, category: str, mood: str = "") -> bytes:
        if category and category.lower() != "random":
            url = f"{self.api_url}search.php"
            params = {"s": category}
            print(f"⏳ Searching TheMealDB for '{category}'...")
            data = self._fetch_json(url, params=params)
            meals = data.get("meals")
            if not meals:
                raise RuntimeError(f"❌ No meals found for '{category}'.")
            meal = random.choice(meals)
        else:
            url = f"{self.api_url}random.php"
            print(f"⏳ Fetching random meal from TheMealDB...")
            data = self._fetch_json(url)
            meals = data.get("meals")
            if not meals:
                raise RuntimeError("❌ No meal returned from API.")
            meal = meals[0]

        image_url = meal.get("strMealThumb")
        name = meal.get("strMeal", "Unknown")
        print(f"   Selected: {name}")

        if not image_url:
            raise RuntimeError("❌ No image URL found.")

        return self._download_bytes(image_url)


class TheCocktailDbProvider(ImageProvider):
    """Image provider for TheCocktailDB."""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("THECOCKTAILDB_API_KEY", "1")
        self.api_url = f"https://www.thecocktaildb.com/api/json/v1/{self.api_key}/"

    def get_name(self) -> str:
        return "TheCocktailDB"

    def get_description(self) -> str:
        return "Random Cocktails and Drinks"

    def download_image(self, category: str, mood: str = "") -> bytes:
        if category and category.lower() != "random":
            url = f"{self.api_url}search.php"
            params = {"s": category}
            print(f"⏳ Searching TheCocktailDB for '{category}'...")
            data = self._fetch_json(url, params=params)
            drinks = data.get("drinks")
            if not drinks:
                raise RuntimeError(f"❌ No drinks found for '{category}'.")
            drink = random.choice(drinks)
        else:
            url = f"{self.api_url}random.php"
            print(f"⏳ Fetching random drink from TheCocktailDB...")
            data = self._fetch_json(url)
            drinks = data.get("drinks")
            if not drinks:
                raise RuntimeError("❌ No drink returned from API.")
            drink = drinks[0]

        image_url = drink.get("strDrinkThumb")
        name = drink.get("strDrink", "Unknown")
        print(f"   Selected: {name}")

        if not image_url:
            raise RuntimeError("❌ No image URL found.")

        return self._download_bytes(image_url)


class GeneratedPeopleProvider(ImageProvider):
    """Image provider for ThisPersonDoesNotExist."""

    def __init__(self):
        super().__init__()
        self.url = "https://thispersondoesnotexist.com/"

    def get_name(self) -> str:
        return "ThisPersonDoesNotExist"

    def get_description(self) -> str:
        return "AI Generated People"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Fetching AI generated person...")
        # Note: This site returns the image bytes directly.
        # It also might require User-Agent.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = self.session.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()
            print("✅ Download successful!")
            return response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download image: {e}")


class TheSportsDbProvider(ImageProvider):
    """Image provider for TheSportsDB."""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("THESPORTSDB_API_KEY", "3")
        self.api_url = f"https://www.thesportsdb.com/api/v1/json/{self.api_key}/searchplayers.php"
        self.famous_players = [
            "Lionel Messi", "Cristiano Ronaldo", "LeBron James", "Stephen Curry",
            "Tom Brady", "Tiger Woods", "Roger Federer", "Serena Williams",
            "Michael Jordan", "Usain Bolt", "Neymar", "Kylian Mbappe"
        ]

    def get_name(self) -> str:
        return "TheSportsDB"

    def get_description(self) -> str:
        return "Sports Players (Search or Random Famous)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        query = category
        if not query or query.lower() == "random":
            query = random.choice(self.famous_players)
            print(f"🎲 Randomly selected player: {query}")

        print(f"⏳ Searching TheSportsDB for '{query}'...")
        params = {"p": query}

        data = self._fetch_json(self.api_url, params=params)
        players = data.get("player")

        if not players:
             raise RuntimeError(f"❌ No players found for '{query}'.")

        # Filter players with strThumb or strCutout (prefer Thumb)
        valid_players = [p for p in players if p.get("strThumb")]

        if not valid_players:
             raise RuntimeError(f"❌ No player images found for '{query}'.")

        player = valid_players[0] # Best match usually first

        image_url = player.get("strThumb")
        name = player.get("strPlayer", "Unknown")
        print(f"   Selected: {name}")

        return self._download_bytes(image_url)


class RandomMetaProvider(ImageProvider):
    """Meta-provider that selects a random provider."""

    def __init__(self, providers_dict: dict, categories_dict: dict, moods_dict: dict):
        super().__init__()
        self.providers = providers_dict
        self.categories = categories_dict
        self.moods = moods_dict

    def get_name(self) -> str:
        return "🎲 Random Source"

    def get_description(self) -> str:
        return "Surprise me! (Random Provider)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Filter out self (ID "0") to avoid recursion
        valid_keys = [k for k in self.providers.keys() if k != "0"]
        if not valid_keys:
             raise RuntimeError("❌ No other providers available.")

        pid = random.choice(valid_keys)
        provider = self.providers[pid]
        p_name = provider.get_name()

        # Determine category
        # If user passed "random", pick a random category for this provider
        target_cat = category
        if category.lower() == "random":
            cats = self.categories.get(p_name, ["Random"])
            if cats:
                target_cat = random.choice(cats)
            else:
                target_cat = "Random"

        # Determine mood
        target_mood = mood
        if not mood:
             moods = self.moods.get(p_name, [""])
             if moods:
                 target_mood = random.choice(moods)

        print(f"🎲 Randomly selected: {p_name} -> {target_cat}")
        return provider.download_image(target_cat, target_mood)


class ClevelandMuseumProvider(ImageProvider):
    """Image provider for Cleveland Museum of Art."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://openaccess-api.clevelandart.org/api/artworks/"

    def get_name(self) -> str:
        return "Cleveland Museum of Art"

    def get_description(self) -> str:
        return "Open Access Art from CMA"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Search parameters
        params = {
            "has_image": 1,
            "limit": 1,
            "skip": random.randint(0, 1000)
        }

        if category and category.lower() != "random":
             params["q"] = category
             params["skip"] = random.randint(0, 20)

        print(f"⏳ Searching Cleveland Museum ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        items = data.get("data", [])
        if not items:
            raise RuntimeError(f"❌ No artworks found for '{category}'.")

        item = items[0]
        images = item.get("images", {})
        # Try web or print
        image_url = images.get("web", {}).get("url") or images.get("print", {}).get("url")

        if not image_url:
             raise RuntimeError("❌ No image URL found in CMA response.")

        title = item.get("title", "Unknown")
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)


class DisneyProvider(ImageProvider):
    """Image provider for Disney API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.disneyapi.dev/character"

    def get_name(self) -> str:
        return "Disney"

    def get_description(self) -> str:
        return "Disney Characters"

    def download_image(self, category: str, mood: str = "") -> bytes:
        params = {"pageSize": 1}

        if category and category.lower() != "random":
            params["name"] = category
        else:
            # Random page (Total ~7438)
            params["page"] = random.randint(1, 7000)

        print(f"⏳ Fetching Disney character ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        items = data.get("data")
        item = None

        if isinstance(items, list):
            if not items:
                 raise RuntimeError(f"❌ No characters found for '{category}'.")
            item = items[0]
        elif isinstance(items, dict):
            item = items
        else:
             raise RuntimeError("❌ Unexpected Disney API response.")

        image_url = item.get("imageUrl")
        name = item.get("name", "Unknown")
        print(f"   Selected: {name}")

        if not image_url:
            raise RuntimeError("❌ No image URL found.")

        return self._download_bytes(image_url)


class WaifuPicsProvider(ImageProvider):
    """Image provider for Waifu.pics."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.waifu.pics/sfw"

    def get_name(self) -> str:
        return "Waifu.pics"

    def get_description(self) -> str:
        return "Anime images (Waifu.pics)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        cat = category.lower()
        if cat == "random":
            cat = "waifu"

        url = f"{self.base_url}/{cat}"
        print(f"⏳ Fetching from Waifu.pics ({cat})...")

        try:
             data = self._fetch_json(url)
        except RuntimeError:
             if cat != "waifu":
                 print(f"   Category '{cat}' not found, falling back to 'waifu'...")
                 url = f"{self.base_url}/waifu"
                 data = self._fetch_json(url)
             else:
                 raise

        image_url = data.get("url")
        if not image_url:
            raise RuntimeError("❌ No image URL returned.")

        return self._download_bytes(image_url)


class HarryPotterProvider(ImageProvider):
    """Image provider for HP-API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://hp-api.onrender.com/api/characters"

    def get_name(self) -> str:
        return "Harry Potter"

    def get_description(self) -> str:
        return "Harry Potter Characters"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Fetching Harry Potter characters...")
        data = self._fetch_json(self.api_url)

        valid_chars = [c for c in data if c.get("image")]

        if not valid_chars:
             raise RuntimeError("❌ No characters with images found.")

        if category and category.lower() != "random":
            filtered = [c for c in valid_chars if category.lower() in c.get("name", "").lower() or category.lower() in c.get("house", "").lower()]
            if filtered:
                valid_chars = filtered
            else:
                 print(f"   No match for '{category}', picking random...")

        chosen = random.choice(valid_chars)
        image_url = chosen.get("image")
        name = chosen.get("name", "Unknown")
        print(f"   Selected: {name}")

        return self._download_bytes(image_url)


class KitsuProvider(ImageProvider):
    """Image provider for Kitsu Anime."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://kitsu.io/api/edge/anime"

    def get_name(self) -> str:
        return "Kitsu"

    def get_description(self) -> str:
        return "Anime Posters (Kitsu)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        params = {"page[limit]": 1}

        if category and category.lower() != "random":
             params["filter[text]"] = category
        else:
             params["page[offset]"] = random.randint(0, 12000)

        print(f"⏳ Fetching from Kitsu ({category})...")
        data = self._fetch_json(self.api_url, params=params)

        items = data.get("data", [])
        if not items:
             raise RuntimeError(f"❌ No anime found for '{category}'.")

        item = items[0]
        attrs = item.get("attributes", {})

        images = attrs.get("coverImage") or attrs.get("posterImage")

        if not images:
             raise RuntimeError("❌ No images found for this anime.")

        image_url = images.get("original") or images.get("large")

        title = attrs.get("canonicalTitle", "Unknown")
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)


class SpaceXProvider(ImageProvider):
    """Image provider for SpaceX."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.spacexdata.com/v4/launches"

    def get_name(self) -> str:
        return "SpaceX"

    def get_description(self) -> str:
        return "SpaceX Launch Photos"

    def download_image(self, category: str, mood: str = "") -> bytes:
        items = []

        if category.lower() == "latest":
             url = f"{self.api_url}/latest"
             print(f"⏳ Fetching latest SpaceX launch...")
             data = self._fetch_json(url)

             links = data.get("links", {}).get("flickr", {})
             if links.get("original"):
                 items = [data]
             else:
                 print("   Latest launch has no images, searching past launches...")

        if not items:
             # Search for random launch with images
             url = f"{self.api_url}/query"
             query = {
                 "query": {
                     "links.flickr.original": { "$ne": [] }
                 },
                 "options": {
                     "limit": 1,
                     "page": random.randint(1, 100),
                     "select": ["name", "links"]
                 }
             }
             if category.lower() != "latest":
                 print(f"⏳ Searching SpaceX launches...")

             try:
                 response = self.session.post(url, json=query, timeout=15)
                 response.raise_for_status()
                 data = response.json()
                 items = data.get("docs", [])
             except Exception as e:
                 print(f"   Query failed: {e}")
                 # Fallback to latest if we haven't tried it already
                 if category.lower() != "latest":
                     url = f"{self.api_url}/latest"
                     data = self._fetch_json(url)
                     items = [data]

        if not items:
             raise RuntimeError("❌ No SpaceX launches with images found.")

        item = items[0]
        links = item.get("links", {}).get("flickr", {})
        images = links.get("original", [])

        if not images:
             raise RuntimeError("❌ No images found for this launch.")

        image_url = random.choice(images)
        name = item.get("name", "Unknown")
        print(f"   Selected: {name}")

        return self._download_bytes(image_url)


class DummyJsonProvider(ImageProvider):
    """Image provider for DummyJSON."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://dummyjson.com/image"
        self.width = 1920
        self.height = 1080

    def get_name(self) -> str:
        return "DummyJSON"

    def get_description(self) -> str:
        return "Placeholder Images (DummyJSON)"

    def set_resolution(self, resolution: str):
        try:
            if "x" in resolution:
                parts = resolution.lower().split("x")
                if len(parts) >= 2:
                    self.width = int(parts[0])
                    self.height = int(parts[1])
        except ValueError:
            pass

    def download_image(self, category: str, mood: str = "") -> bytes:
        url = f"{self.base_url}/{self.width}x{self.height}"
        text = category
        if category.lower() == "random":
             text = "Random Image"

        params = {"text": text}
        print(f"⏳ Downloading from DummyJSON...")

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Failed to download: {e}")

class PokeApiProvider(ImageProvider):
    """Image provider for PokeAPI."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://pokeapi.co/api/v2/pokemon"

    def get_name(self) -> str:
        return "PokeAPI"

    def get_description(self) -> str:
        return "Pokemon Official Artwork"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # If category is random, pick a random ID (1-1010)
        # If category is a name, search for it.

        name_or_id = category.lower()
        if name_or_id == "random":
            name_or_id = str(random.randint(1, 1010))

        url = f"{self.api_url}/{name_or_id}"
        print(f"⏳ Fetching Pokemon ({name_or_id})...")

        try:
            data = self._fetch_json(url)
        except RuntimeError as e:
            if "404" in str(e):
                raise RuntimeError(f"❌ Pokemon '{category}' not found.")
            raise e

        sprites = data.get("sprites", {})
        other = sprites.get("other", {})
        official = other.get("official-artwork", {})
        image_url = official.get("front_default")

        if not image_url:
            # Fallback to home (high res) or default
            home = other.get("home", {})
            image_url = home.get("front_default") or sprites.get("front_default")

        if not image_url:
             raise RuntimeError("❌ No image found for this Pokemon.")

        name = data.get("name", "Unknown").title()
        print(f"   Selected: {name}")

        return self._download_bytes(image_url)


class GhibliProvider(ImageProvider):
    """Image provider for Studio Ghibli API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://ghibliapi.vercel.app/films"

    def get_name(self) -> str:
        return "Studio Ghibli"

    def get_description(self) -> str:
        return "Studio Ghibli Movie Banners"

    def download_image(self, category: str, mood: str = "") -> bytes:
        print(f"⏳ Fetching Ghibli movies...")
        data = self._fetch_json(self.api_url)

        if not data:
            raise RuntimeError("❌ No data returned from Ghibli API.")

        # Filter by title if category is specific
        if category and category.lower() != "random":
            filtered = [m for m in data if category.lower() in m.get("title", "").lower()]
            if filtered:
                data = filtered
            else:
                print(f"   No match for '{category}', picking random...")

        movie = random.choice(data)

        # Prefer movie_banner (landscape) over image (poster)
        image_url = movie.get("movie_banner") or movie.get("image")

        if not image_url:
             raise RuntimeError("❌ No image URL found for this movie.")

        title = movie.get("title", "Unknown")
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)


class DigimonProvider(ImageProvider):
    """Image provider for Digimon API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://digi-api.com/api/v1/digimon"

    def get_name(self) -> str:
        return "Digimon"

    def get_description(self) -> str:
        return "Digimon Characters"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # If random, pick ID 1-1400
        query = category
        if category.lower() == "random":
             query = str(random.randint(1, 1400))

        url = f"{self.api_url}/{query}"
        print(f"⏳ Fetching Digimon ({query})...")

        try:
            data = self._fetch_json(url)
        except RuntimeError as e:
            if "404" in str(e):
                raise RuntimeError(f"❌ Digimon '{category}' not found.")
            raise e

        images = data.get("images", [])
        if not images:
             raise RuntimeError("❌ No images found for this Digimon.")

        image_url = images[0].get("href")

        if not image_url:
             raise RuntimeError("❌ No image URL found.")

        name = data.get("name", "Unknown")
        print(f"   Selected: {name}")

        return self._download_bytes(image_url)


class ZeldaCompendiumProvider(ImageProvider):
    """Image provider for Hyrule Compendium (Zelda BOTW)."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://botw-compendium.herokuapp.com/api/v3/compendium/entry"

    def get_name(self) -> str:
        return "Zelda (BOTW)"

    def get_description(self) -> str:
        return "Breath of the Wild Compendium"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # If category is random, pick a random ID (1-389)
        # Note: IDs go up to 389 for creatures/monsters/treasure.
        # Actually there are more categories.
        # Let's just pick a random ID.

        entry_id = category
        if category.lower() == "random":
            entry_id = str(random.randint(1, 389))

        # If it's a name, the API supports name lookups too?
        # "entry/{entry_name_or_id}"

        url = f"{self.api_url}/{entry_id}"
        print(f"⏳ Fetching Zelda Compendium entry ({entry_id})...")

        try:
            response = self._fetch_json(url)
        except RuntimeError as e:
             if "404" in str(e): # Handle not found
                 raise RuntimeError(f"❌ Entry '{category}' not found.")
             raise e

        data = response.get("data", {})
        image_url = data.get("image")

        if not image_url:
             raise RuntimeError("❌ No image found for this entry.")

        name = data.get("name", "Unknown").title()
        print(f"   Selected: {name}")

        return self._download_bytes(image_url)

class MinecraftSkinProvider(ImageProvider):
    """Image provider for Minecraft Skins (Minotar)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://minotar.net/armor/body"
        self.width = 1920
        self.famous_players = [
            "Notch", "Jeb_", "Dream", "Technoblade", "Grian",
            "MumboJumbo", "CaptainSparklez", "TommyInnit", "Philza",
            "DanTDM", "Stampy", "LDShadowLady", "SethBling", "Etho"
        ]

    def get_name(self) -> str:
        return "Minecraft Skins"

    def get_description(self) -> str:
        return "Minecraft Player Skins (Minotar)"

    def set_resolution(self, resolution: str):
        try:
            if "x" in resolution:
                parts = resolution.lower().split("x")
                if len(parts) >= 1:
                    self.width = int(parts[0])
        except ValueError:
            pass

    def download_image(self, category: str, mood: str = "") -> bytes:
        user = category
        if user.lower() == "random":
             user = random.choice(self.famous_players)

        url = f"{self.base_url}/{user}/{self.width}.png"
        print(f"⏳ Downloading Minecraft skin for '{user}'...")

        # Minotar returns 200 even for invalid users (steve skin), but that's fine.
        return self._download_bytes(url)

class YugiohProvider(ImageProvider):
    """Image provider for Yu-Gi-Oh! Cards."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://db.ygoprodeck.com/api/v7"

    def get_name(self) -> str:
        return "Yu-Gi-Oh!"

    def get_description(self) -> str:
        return "Yu-Gi-Oh! Card Art"

    def download_image(self, category: str, mood: str = "") -> bytes:
        if category and category.lower() != "random":
            # Search
            url = f"{self.api_url}/cardinfo.php"
            params = {"fname": category}
            print(f"⏳ Searching Yu-Gi-Oh! for '{category}'...")

            data = self._fetch_json(url, params=params)
            data = data.get("data", [])
            if not data:
                raise RuntimeError(f"❌ No cards found for '{category}'.")

            card = random.choice(data)
        else:
            # Random
            url = f"{self.api_url}/randomcard.php"
            print(f"⏳ Fetching random Yu-Gi-Oh! card...")
            data = self._fetch_json(url)

            if isinstance(data, dict) and "data" in data:
                 card = data["data"][0]
            elif isinstance(data, list):
                 card = data[0]
            else:
                 card = data

        images = card.get("card_images", [])
        if not images:
             raise RuntimeError("❌ No images found for this card.")

        image_url = images[0].get("image_url")
        name = card.get("name", "Unknown")
        print(f"   Selected: {name}")

        return self._download_bytes(image_url)

class iTunesArtworkProvider(ImageProvider):
    """Image provider for iTunes Artwork (High Res)."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://itunes.apple.com/search"
        self.random_terms = [
            "Rock", "Pop", "Jazz", "Classical", "Metal", "Hip Hop",
            "Taylor Swift", "Beatles", "Queen", "Drake", "Coldplay",
            "Movie", "Action", "Comedy", "Thriller", "Sci-Fi"
        ]

    def get_name(self) -> str:
        return "iTunes Artwork"

    def get_description(self) -> str:
        return "Album & Movie Artwork (High Res)"

    def download_image(self, category: str, mood: str = "") -> bytes:
        term = category
        if term.lower() == "random":
             term = random.choice(self.random_terms)

        params = {
            "term": term,
            "media": "all",
            "limit": 50
        }

        print(f"⏳ Searching iTunes for '{term}'...")
        data = self._fetch_json(self.api_url, params=params)

        results = data.get("results", [])
        if not results:
             raise RuntimeError(f"❌ No results found for '{term}'.")

        valid_results = [r for r in results if r.get("artworkUrl100")]

        if not valid_results:
             raise RuntimeError(f"❌ No artwork found for '{term}'.")

        chosen = random.choice(valid_results)

        art_url = chosen["artworkUrl100"]
        # Hack for high res
        image_url = art_url.replace("100x100bb", "10000x10000bb")

        title = chosen.get("trackName") or chosen.get("collectionName", "Unknown")
        artist = chosen.get("artistName", "")
        if artist:
            title = f"{title} by {artist}"

        print(f"   Selected: {title}")

        return self._download_bytes(image_url)

class WikipediaProvider(ImageProvider):
    """Image provider for Wikipedia."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://en.wikipedia.org/w/api.php"
        # Wikipedia requires a User-Agent
        self.session.headers.update({
            "User-Agent": "EasyWallpaper/1.0 (mailto:test@example.com)"
        })

    def get_name(self) -> str:
        return "Wikipedia"

    def get_description(self) -> str:
        return "Encyclopedic images from Wikipedia"

    def download_image(self, category: str, mood: str = "") -> bytes:
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original"
        }

        if category.lower() == "random":
            params["generator"] = "random"
            params["grnnamespace"] = 0
            params["grnlimit"] = 10
            print("⏳ Fetching random pages from Wikipedia...")
        else:
            params["titles"] = category
            print(f"⏳ Searching Wikipedia for '{category}'...")

        try:
            data = self._fetch_json(self.api_url, params=params)
        except RuntimeError as e:
            if "JSON" in str(e):
                # Sometimes Wiki returns HTML error pages if overloaded
                raise RuntimeError("❌ Wikipedia API error (Check your connection or try again).")
            raise e

        pages = data.get("query", {}).get("pages", {})
        if not pages:
             raise RuntimeError(f"❌ No results found for '{category}'.")

        # Find a page with an original image
        valid_pages = []
        for pid, page in pages.items():
            if "original" in page:
                 source = page["original"]["source"]
                 # Filter common non-wallpaper extensions (e.g. .pdf, .svg, .tif)
                 # We prefer .jpg, .png
                 if source.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                     valid_pages.append(page)

        if not valid_pages:
             if category.lower() == "random":
                  # Try again? Recursion limited to 1
                  # Or just raise
                  raise RuntimeError("❌ No valid images found in random selection.")
             else:
                  raise RuntimeError(f"❌ No images found for '{category}'.")

        chosen = random.choice(valid_pages)
        image_url = chosen["original"]["source"]
        title = chosen.get("title", "Unknown")
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)


class LibraryOfCongressProvider(ImageProvider):
    """Image provider for Library of Congress."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://www.loc.gov/photos/"

    def get_name(self) -> str:
        return "Library of Congress"

    def get_description(self) -> str:
        return "Historical prints and photos"

    def download_image(self, category: str, mood: str = "") -> bytes:
        # Search with random pagination
        # Page 1 to 5 usually covers best results for broad terms
        page = random.randint(1, 5)

        params = {
            "q": category if category.lower() != "random" else "history",
            "fo": "json",
            "c": 20, # count
            "sp": page # page number
        }

        print(f"⏳ Searching Library of Congress ({params['q']}, page {page})...")
        try:
             # LoC API sometimes is slow
             data = self._fetch_json(self.api_url, params=params)
        except RuntimeError:
             # Fallback to page 1 if random page fails (e.g. out of range)
             if page != 1:
                 print("   Page empty, trying page 1...")
                 params["sp"] = 1
                 data = self._fetch_json(self.api_url, params=params)
             else:
                 raise

        results = data.get("results", [])
        if not results:
             raise RuntimeError(f"❌ No results found for '{category}'.")

        # Filter for valid images
        valid_images = []
        for item in results:
            if "image_url" in item and item["image_url"]:
                # image_url is a list of URLs, ascending in size usually.
                # We want the largest available.
                # Sometimes the last one is a .tif which we can't display easily?
                # Usually they are .jpg or .gif
                # Let's check the last one.
                urls = item["image_url"]
                if not urls: continue

                # Prefer the largest jpg
                best_url = None
                for u in reversed(urls):
                    if u.lower().endswith(".jpg") or u.lower().endswith(".jpeg") or u.lower().endswith(".png"):
                        best_url = u
                        break

                if best_url:
                    valid_images.append((best_url, item.get("title", "Unknown")))

        if not valid_images:
             raise RuntimeError(f"❌ No valid images found for '{category}'.")

        image_url, title = random.choice(valid_images)
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)


class FlickrProvider(ImageProvider):
    """Image provider for Flickr Public Feed."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://www.flickr.com/services/feeds/photos_public.gne"

    def get_name(self) -> str:
        return "Flickr"

    def get_description(self) -> str:
        return "Public photos from Flickr"

    def download_image(self, category: str, mood: str = "") -> bytes:
        tags = category
        if category.lower() == "random":
            # Just pick a random common tag
            tags = random.choice(["nature", "city", "travel", "architecture", "street", "art", "night", "landscape"])

        if mood:
            tags = f"{tags},{mood}"

        params = {
            "format": "json",
            "tags": tags,
            "nojsoncallback": 1,
            "lang": "en-us"
        }

        print(f"⏳ Searching Flickr ({tags})...")
        data = self._fetch_json(self.api_url, params=params)

        items = data.get("items", [])
        if not items:
             raise RuntimeError(f"❌ No photos found for '{tags}' on Flickr.")

        item = random.choice(items)
        media = item.get("media", {})
        # Flickr feed returns 'm' size (small). We hack the URL to get 'b' (large) or 'h' (huge).
        image_url = media.get("m")

        if not image_url:
             raise RuntimeError("❌ No image URL found.")

        # Try to upgrade resolution
        # Suffixes: _m.jpg -> _b.jpg (1024)
        if "_m." in image_url:
            image_url = image_url.replace("_m.", "_b.")

        title = item.get("title", "Unknown")
        print(f"   Selected: {title}")

        return self._download_bytes(image_url)
