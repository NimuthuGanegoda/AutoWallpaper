"""
Configuration constants for easy-wallpaper.

Defines categories, moods, resolutions, and provider mapping.
"""

from providers import (
    PexelsProvider,
    PixabayProvider,
    WaifuImProvider,
    CatgirlProvider,
    WallhavenProvider,
    BingProvider,
    UnsplashProvider,
    PicsumProvider
)

# Provider mapping
PROVIDERS = {
    "1": PexelsProvider(),
    "2": PixabayProvider(),
    "3": WaifuImProvider(),
    "4": CatgirlProvider(),
    "5": WallhavenProvider(),
    "6": BingProvider(),
    "7": UnsplashProvider(),
    "8": PicsumProvider(),
}

# Categories for each provider
CATEGORIES = {
    "Pexels": [
        "nature",
        "landscape",
        "urban",
        "beach",
        "mountain",
        "forest",
        "city",
        "sky",
    ],
    "Pixabay": [
        "abstract",
        "animals",
        "art",
        "backgrounds",
        "buildings",
        "business",
        "computer",
        "food",
        "nature",
        "people",
        "places",
        "science",
        "technology",
    ],
    "waifu.im": [
        "waifu",
        "maid",
        "miko",
        "oppai",
        "uniform",
        "kitsune",
        "demon",
        "elf",
    ],
    "nekos.moe": [
        "safe sfw",
        "nsfw",
        "mixed",
    ],
    "Wallhaven": [
        "general",
        "anime",
        "people",
        "fantasy",
        "scifi",
        "nature",
        "minimalist",
        "cyberpunk",
    ],
    "Bing": [
        "daily",
    ],
    "Unsplash": [
        "nature",
        "wallpapers",
        "travel",
        "animals",
        "architecture",
        "texture",
    ],
    "Picsum": [
        "random",
        "nature",
        "tech",
        "people",
    ],
}

# Moods for filtering
MOODS = {
    "Pexels": ["calm", "vibrant", "dark", "bright"],
    "Pixabay": ["colorful", "minimal", "artistic", "realistic"],
    "waifu.im": [""],
    "nekos.moe": [""],
    "Wallhaven": [""],
    "Bing": [""],
    "Unsplash": ["black_and_white", "high_key", "low_key"],
    "Picsum": ["grayscale", "blur"],
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
