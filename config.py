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

# Provider mapping
PROVIDERS = {
    "1": PexelsProvider(),
    "2": PixabayProvider(),
    "3": UnsplashProvider(),
    "4": WallhavenProvider(),
    "5": BingProvider(),
    "6": PicsumProvider(),
    "7": WaifuImProvider(),
    "8": CatgirlProvider(),
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
    "Unsplash": [
        "nature",
        "wallpapers",
        "travel",
        "architecture",
        "textures",
        "animals",
        "food",
        "fashion",
    ],
    "Wallhaven": [
        "anime",
        "general",
        "people",
        "fantasy",
        "scifi",
        "cyberpunk",
    ],
    "Bing": [
        "daily",
        "random",
    ],
    "Picsum": [
        "random",
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
}

# Moods for filtering
MOODS = {
    "Pexels": ["calm", "vibrant", "dark", "bright"],
    "Pixabay": ["colorful", "minimal", "artistic", "realistic"],
    "Unsplash": ["landscape", "portrait"], # Unsplash API allows orientation, mapping here for simplicity
    "Wallhaven": ["sfw", "sketchy", "nsfw"],
    "Bing": [],
    "Picsum": ["normal", "grayscale", "blur"],
    "waifu.im": [""],
    "nekos.moe": [""],
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
DEFAULT_PROVIDER = "7"  # waifu.im
DEFAULT_CATEGORY = "waifu"
DEFAULT_RESOLUTION = "1920x1080"
