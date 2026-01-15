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
    WallhavenProvider,
    BingProvider,
    PicsumProvider
)

# Default values
DEFAULT_PROVIDER = "3"  # waifu.im
DEFAULT_CATEGORY = "waifu"
DEFAULT_RESOLUTION = "1920x1080"

# Provider mapping
PROVIDERS = {
    "1": PexelsProvider(),
    "2": PixabayProvider(),
    "3": WaifuImProvider(),
    "4": CatgirlProvider(),
    "5": UnsplashProvider(),
    "6": WallhavenProvider(),
    "7": BingProvider(),
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
    "Unsplash": [
        "nature",
        "wallpapers",
        "travel",
        "architecture",
        "textures",
        "random"
    ],
    "Wallhaven": [
        "anime",
        "fantasy",
        "cyberpunk",
        "scenery",
        "digital art"
    ],
    "Bing": [
        "0", # Today
        "1", # Yesterday
        "2",
        "3",
        "4",
        "5",
        "6",
        "7"
    ],
    "Picsum": [
        "random",
        "nature",
        "tech",
        "people"
    ]
}

# Moods for filtering
MOODS = {
    "Pexels": ["calm", "vibrant", "dark", "bright"],
    "Pixabay": ["colorful", "minimal", "artistic", "realistic"],
    "waifu.im": [""],
    "nekos.moe": [""],
    "Unsplash": ["dark", "light", "black_and_white"],
    "Wallhaven": [""],
    "Bing": [""],
    "Picsum": [""]
}

# Resolution options
RESOLUTIONS = [
    "1920x1080",
    "1366x768",
    "1280x720",
    "2560x1440",
    "3840x2160",
]
