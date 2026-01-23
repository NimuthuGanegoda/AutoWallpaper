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
    PicsumProvider,
    NasaApodProvider,
    TheCatApiProvider,
    TheDogApiProvider,
    MetMuseumProvider,
)

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
    "9": NasaApodProvider(),
    "10": TheCatApiProvider(),
    "11": TheDogApiProvider(),
    "12": MetMuseumProvider(),
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
        "people",
        "street-photography",
        "animals",
        "architecture",
    ],
    "Wallhaven": [
        "anime",
        "general",
        "people",
        "fantasy",
        "cyberpunk",
        "nature",
        "scifi",
    ],
    "Bing": [
        "Today",
        "Yesterday",
        "2 days ago",
        "3 days ago",
        "4 days ago",
        "5 days ago",
        "6 days ago",
        "7 days ago",
    ],
    "Picsum": [
        "random",
        "seed",
    ],
    "NASA APOD": [
        "Today",
        "Random",
    ],
    "TheCatAPI": [
        "Random",
    ],
    "TheDogAPI": [
        "Random",
    ],
    "The Met": [
        "sunflowers",
        "landscape",
        "portrait",
        "arms and armor",
        "egyptian",
        "asian art",
        "islamic art",
        "modern art",
    ],
}

# Moods for filtering
MOODS = {
    "Pexels": ["calm", "vibrant", "dark", "bright"],
    "Pixabay": ["colorful", "minimal", "artistic", "realistic"],
    "waifu.im": [""],
    "nekos.moe": [""],
    "Unsplash": ["dark", "light", "colorful", "black_and_white"],
    "Wallhaven": [""],
    "Bing": [""],
    "Picsum": [""],
    "NASA APOD": [""],
    "TheCatAPI": [""],
    "TheDogAPI": [""],
    "The Met": [""],
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
