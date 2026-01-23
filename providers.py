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
        if "yesterday" in cat_lower:
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
