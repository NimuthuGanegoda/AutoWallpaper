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
    UnsplashProvider
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
        "raiden-shogun",
    ],
    "nekos.moe": [
        "safe sfw",
        "nsfw",
        "mixed",
    ],
    "Wallhaven": [
        "anime",
        "fantasy",
        "games",
        "nature",
        "cyberpunk",
        "city",
        "cars",
        "minimalism",
    ],
    "Bing Daily": [
        "today",
        "yesterday",
        "2 days ago",
        "3 days ago",
        "4 days ago",
        "5 days ago",
        "6 days ago",
    ],
    "Unsplash": [
        "nature",
        "wallpapers",
        "travel",
        "architecture",
        "street-photography",
        "film",
        "animals",
        "food-drink",
        "people",
    ]
}

# Moods for filtering
MOODS = {
    "Pexels": ["calm", "vibrant", "dark", "bright"],
    "Pixabay": ["colorful", "minimal", "artistic", "realistic"],
    "waifu.im": [""],
    "nekos.moe": [""],
    "Wallhaven": ["random", "toplist", "views", "favorites", "relevance"],
    "Bing Daily": [""],
    "Unsplash": ["dark", "light", "black_and_white"], # Could also be mapped to orientation or other params but queries work well
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
