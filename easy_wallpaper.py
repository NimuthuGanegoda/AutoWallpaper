#!/usr/bin/env python3
"""
easy-wallpaper: A simple CLI tool to download and set desktop wallpapers.

This tool interactively asks the user for wallpaper preferences (category, 
resolution, mood, and image provider) and downloads a random image, then sets 
it as the desktop wallpaper on Windows, macOS, or Linux (GNOME).

Supported providers:
- Pexels (no API key required)
- Pixabay (no API key required)
"""

import os
import platform
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

import requests


# ============================================================================
# Image Provider Abstraction
# ============================================================================

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


class PexelsProvider(ImageProvider):
    """Image provider for Pexels API."""
    
    def __init__(self):
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
        
        params = {
            "key": self.api_key,
            "q": query,
            "per_page": 1,
            "image_type": "photo",
        }
        
        try:
            print(f"⏳ Downloading from Pixabay ({query})...")
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("hits"):
                raise RuntimeError(f"❌ No images found for '{query}' on Pixabay.")
            
            image_data = data["hits"][0]
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
    
    def download_image(self, category: str, mood: str = "") -> bytes:
        """Download image from waifu.im."""
        # Map categories to waifu.im tags
        waifu_tags = self._map_category_to_tags(category)
        
        params = {
            "included_tags": ",".join(waifu_tags),
            "is_nsfw": "false",
        }
        
        # Add orientation preference
        params["orientation"] = "landscape"
        
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
        # Common waifu.im tags
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
        
        # Check if category is directly in map
        if category_lower in tag_map:
            return tag_map[category_lower]
        
        # Check for partial matches
        for key in tag_map:
            if key in category_lower:
                return tag_map[key]
        
        # Default to waifu tag for unknown categories
        return ["waifu"]


# ============================================================================
# Provider Registry
# ============================================================================

PROVIDERS = {
    "1": PexelsProvider,
    "2": PixabayProvider,
    "3": WaifuImProvider,
}


# ============================================================================
# Configuration
# ============================================================================

# Wallpaper categories and moods for user guidance
CATEGORIES = [
    "nature", "space", "cyberpunk", "architecture", "forest",
    "ocean", "mountains", "abstract", "city", "animals"
]

MOODS = [
    "dark", "light", "vibrant", "minimalist", "colorful", "calm"
]

RESOLUTIONS = {
    "1": ("1920x1080", "1920x1080"),
    "2": ("2560x1440", "2560x1440"),
    "3": ("3840x2160", "3840x2160"),
    "4": ("custom", None),
}


# ============================================================================
# User Input Functions
# ============================================================================

def get_provider() -> ImageProvider:
    """
    Prompt the user to select an image provider.
    
    Returns:
        ImageProvider: An instance of the selected provider.
    """
    print("\n📷 Available image providers:")
    for key, provider_class in PROVIDERS.items():
        provider = provider_class()
        print(f"  {key}. {provider.get_name():15} - {provider.get_description()}")
    
    while True:
        choice = input("\nSelect provider (1-3): ").strip()
        
        if choice in PROVIDERS:
            return PROVIDERS[choice]()
        else:
            print("❌ Please select a valid option.")


def get_waifu_category() -> str:
    """
    Prompt the user to select a waifu type.
    
    Returns:
        str: The selected waifu category.
    """
    waifu_categories = [
        "waifu", "maid", "miko", "elf", "demon", 
        "kitsune", "oppai", "uniform"
    ]
    
    print("\n🎌 What kind of waifu do you want?")
    for i, cat in enumerate(waifu_categories, 1):
        print(f"  {i}. {cat}")
    print(f"  {len(waifu_categories) + 1}. Custom")
    
    while True:
        try:
            choice = input(f"\nSelect waifu type (1-{len(waifu_categories) + 1}): ").strip()
            choice_idx = int(choice) - 1
            
            if choice_idx < len(waifu_categories):
                return waifu_categories[choice_idx]
            elif choice_idx == len(waifu_categories):
                custom = input("Enter custom waifu tag: ").strip()
                if custom:
                    return custom
                print("❌ Please enter a valid tag.")
            else:
                print("❌ Please select a valid option.")
        except ValueError:
            print("❌ Please enter a number.")


def get_category() -> str:
    """
    Prompt the user to select or enter a wallpaper category.
    
    Returns:
        str: The selected or custom category name.
    """
    print("\n📸 Available categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    print(f"  {len(CATEGORIES) + 1}. Custom category")
    
    while True:
        try:
            choice = input("\nSelect a category (1-11): ").strip()
            choice_idx = int(choice) - 1
            
            if choice_idx < len(CATEGORIES):
                return CATEGORIES[choice_idx]
            elif choice_idx == len(CATEGORIES):
                custom = input("Enter custom category: ").strip()
                if custom:
                    return custom
                print("❌ Please enter a valid category.")
            else:
                print("❌ Please select a valid option.")
        except ValueError:
            print("❌ Please enter a number.")


def get_resolution() -> str:
    """
    Prompt the user to select a resolution or enter a custom one.
    
    Returns:
        str: Resolution in "WIDTHxHEIGHT" format (e.g., "1920x1080").
    """
    print("\n📐 Available resolutions:")
    for key, (label, res) in RESOLUTIONS.items():
        print(f"  {key}. {label}")
    
    while True:
        choice = input("\nSelect resolution (1-4): ").strip()
        
        if choice in RESOLUTIONS:
            _, res = RESOLUTIONS[choice]
            if res:
                return res
            # Handle custom resolution
            custom_res = input("Enter custom resolution (e.g., 1600x900): ").strip()
            if "x" in custom_res or "X" in custom_res:
                return custom_res.lower()
            print("❌ Invalid resolution format. Use WIDTHxHEIGHT.")
        else:
            print("❌ Please select a valid option.")


def get_mood() -> str:
    """
    Optionally prompt the user to select a mood for the wallpaper.
    
    Returns:
        str: The selected mood, or empty string if skipped.
    """
    print("\n🎨 Moods (optional):")
    for i, mood in enumerate(MOODS, 1):
        print(f"  {i}. {mood}")
    print(f"  {len(MOODS) + 1}. Skip")
    
    while True:
        try:
            choice = input("\nSelect mood (1-7) or skip: ").strip()
            choice_idx = int(choice) - 1
            
            if choice_idx < len(MOODS):
                return MOODS[choice_idx]
            elif choice_idx == len(MOODS):
                return ""
            else:
                print("❌ Please select a valid option.")
        except ValueError:
            print("❌ Please enter a number.")


# ============================================================================
# Download Functions
# ============================================================================

def save_wallpaper(image_data: bytes, filename: str = "wallpaper.jpg") -> str:
    """
    Save downloaded wallpaper to the current working directory.
    
    Args:
        image_data: The image file content.
        filename: Filename to save as (default: "wallpaper.jpg").
    
    Returns:
        str: Absolute path to the saved wallpaper file.
    """
    # Save to current working directory
    filepath = Path.cwd() / filename
    
    try:
        with open(filepath, "wb") as f:
            f.write(image_data)
        print(f"💾 Wallpaper saved to: {filepath}")
        return str(filepath)
    except IOError as e:
        raise RuntimeError(f"❌ Failed to save wallpaper: {e}")


# ============================================================================
# OS-Specific Wallpaper Setting Functions
# ============================================================================

def set_wallpaper_windows(filepath: str) -> None:
    """
    Set wallpaper on Windows using ctypes.
    
    Args:
        filepath: Absolute path to the wallpaper image.
    
    Raises:
        RuntimeError: If setting wallpaper fails.
    """
    try:
        import ctypes
        
        # Windows API: SystemParametersInfo with SPI_SETDESKWALLPAPER
        ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 0)
        print("✅ Wallpaper set successfully on Windows!")
    
    except Exception as e:
        raise RuntimeError(f"❌ Failed to set wallpaper on Windows: {e}")


def set_wallpaper_macos(filepath: str) -> None:
    """
    Set wallpaper on macOS using AppleScript via osascript.
    
    Args:
        filepath: Absolute path to the wallpaper image.
    
    Raises:
        RuntimeError: If setting wallpaper fails.
    """
    try:
        script = f'''tell application "System Events"
            set desktopCount to count of desktops
            repeat with desktopNumber from 1 to desktopCount
                tell desktop desktopNumber
                    set picture to "{filepath}"
                end tell
            end repeat
        end tell'''
        
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Wallpaper set successfully on macOS!")
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ Failed to set wallpaper on macOS: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("❌ osascript not found. Make sure you're running macOS.")


def set_wallpaper_linux(filepath: str) -> None:
    """
    Set wallpaper on Linux using GNOME dconf, with fallback to feh/nitrogen.
    
    Args:
        filepath: Absolute path to the wallpaper image.
    
    Raises:
        RuntimeError: If all methods to set wallpaper fail.
    """
    try:
        # Try GNOME Desktop (most common)
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", f"file://{filepath}"],
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{filepath}"],
            check=True,
            capture_output=True
        )
        print("✅ Wallpaper set successfully on Linux (GNOME)!")
        return
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback: try feh (common on lightweight desktops)
    try:
        subprocess.run(
            ["feh", "--bg-scale", filepath],
            check=True,
            capture_output=True
        )
        print("✅ Wallpaper set successfully on Linux (feh)!")
        return
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback: try nitrogen
    try:
        subprocess.run(
            ["nitrogen", "--set-zoom-fill", filepath],
            check=True,
            capture_output=True
        )
        print("✅ Wallpaper set successfully on Linux (nitrogen)!")
        return
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "❌ Could not set wallpaper. Please install gsettings (GNOME), feh, or nitrogen."
        )


def set_wallpaper(filepath: str) -> None:
    """
    Set wallpaper on the current operating system.
    
    Args:
        filepath: Absolute path to the wallpaper image.
    
    Raises:
        RuntimeError: If the OS is not supported or wallpaper setting fails.
    """
    system = platform.system()
    
    if system == "Windows":
        set_wallpaper_windows(filepath)
    elif system == "Darwin":  # macOS
        set_wallpaper_macos(filepath)
    elif system == "Linux":
        set_wallpaper_linux(filepath)
    else:
        raise RuntimeError(f"❌ Unsupported operating system: {system}")


# ============================================================================
# Main Program
# ============================================================================

def main() -> None:
    """
    Main entry point for the easy-wallpaper CLI tool.
    """
    try:
        print("\n" + "=" * 60)
        print("🖼️  Welcome to easy-wallpaper!")
        print("=" * 60)
        
        # Get user preferences
        provider = get_provider()
        
        # Get category based on provider type
        if isinstance(provider, WaifuImProvider):
            category = get_waifu_category()
        else:
            category = get_category()
        
        resolution = get_resolution()
        mood = get_mood()
        
        # Download wallpaper using selected provider
        image_data = provider.download_image(category, mood)
        
        # Save wallpaper
        filepath = save_wallpaper(image_data)
        
        # Set wallpaper
        set_wallpaper(filepath)
        
        print("\n" + "=" * 60)
        print("🎉 All done! Enjoy your new wallpaper!")
        print("=" * 60 + "\n")
    
    except RuntimeError as e:
        print(f"\n{e}\n", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
