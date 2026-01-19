"""
Configuration constants for easy-wallpaper.

Defines categories, moods, resolutions, and provider mapping.
"""

from providers import (
    PexelsProvider,
    PixabayProvider,
    WaifuImProvider,
    CatgirlProvider,
    UnsplashProvider,
    PicsumProvider,
    WallhavenProvider,
    BingProvider
)

# Provider mapping
PROVIDERS = {
    "1": PexelsProvider(),
    "2": PixabayProvider(),
    "3": WaifuImProvider(),
    "4": CatgirlProvider(),
    "5": UnsplashProvider(),
    "6": PicsumProvider(),
    "7": WallhavenProvider(),
    "8": BingProvider(),
}

# Categories for each provider
CATEGORIES = {
    "Pexels": [
        "nature", "landscape", "urban", "beach", "mountain", "forest", "city", "sky",
    ],
    "Pixabay": [
        "abstract", "animals", "art", "backgrounds", "buildings", "business",
        "computer", "food", "nature", "people", "places", "science", "technology",
    ],
    "waifu.im": [
        "waifu", "maid", "miko", "oppai", "uniform", "kitsune", "demon", "elf",
    ],
    "nekos.moe": [
        "safe sfw", "nsfw", "mixed",
    ],
    "Unsplash": [
        "nature", "people", "architecture", "technology", "interiors", "experimental", "fashion", "film", "health", "random"
    ],
    "Picsum": [
        "random", "nature", "city", "tech", "abstract"
    ],
    "Wallhaven": [
        "anime", "general", "people", "fantasy", "scifi", "cyberpunk", "landscape", "horror"
    ],
    "Bing": [
        "today", "yesterday", "2 days ago", "3 days ago", "4 days ago", "5 days ago", "6 days ago", "7 days ago"
    ],
}

# Moods for filtering
MOODS = {
    "Pexels": ["calm", "vibrant", "dark", "bright"],
    "Pixabay": ["colorful", "minimal", "artistic", "realistic"],
    "waifu.im": [""],
    "nekos.moe": [""],
    "Unsplash": ["dark", "light", "black_and_white"],
    "Picsum": [""],
    "Wallhaven": [""],
    "Bing": [""],
}

# Resolution options
RESOLUTIONS = [
    "1920x1080",
    "1366x768",
    "1280x720",
    "2560x1440",
    "3840x2160",
]

# Default values
DEFAULT_PROVIDER = "3"  # waifu.im
DEFAULT_CATEGORY = "waifu"
DEFAULT_RESOLUTION = "1920x1080"
