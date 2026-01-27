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
