#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui import (
    get_provider,
    get_category,
    get_mood,
    get_resolution,
)
from wallpaper import save_wallpaper, set_wallpaper


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Easy Wallpaper Downloader")
    parser.add_argument(
        "--nsfw",
        action="store_true",
        help="Enable NSFW content (waifu.im and nekos.moe)"
    )
    args = parser.parse_args()

    nsfw_allowed = args.nsfw

    print("\n" + "🖼️  " * 12)
    print(" " * 8 + "WELCOME TO EASY WALLPAPER")
    print("🖼️  " * 12)
    print("\nDownload and set beautiful wallpapers effortlessly!")
    
    try:
        if nsfw_allowed:
            print("🔞 NSFW content enabled via command line flag.")

        # Get provider selection
        provider_key, provider = get_provider()
        
        # Get category
        category = get_category(provider.get_name(), nsfw_allowed)
        print(f"✅ Selected category: {category}")
        
        # Get mood (if available)
        mood = get_mood(provider.get_name())
        if mood:
            print(f"✅ Selected mood: {mood}")
        
        # Get resolution preference
        resolution = get_resolution()
        print(f"✅ Selected resolution: {resolution}")
        
        print("\n" + "=" * 50)
        print("⏳ DOWNLOADING WALLPAPER")
        print("=" * 50)
        
        # Download image from provider
        image_data = provider.download_image(category, mood, nsfw=nsfw_allowed)
        
        # Save the wallpaper
        wallpaper_path = save_wallpaper(image_data)
        
        # Set the wallpaper
        print("\n" + "=" * 50)
        print("🎨 SETTING WALLPAPER")
        print("=" * 50)
        set_wallpaper(wallpaper_path)
        
        print("\n" + "=" * 50)
        print("✨ SUCCESS!")
        print("=" * 50)
        print(f"Your new wallpaper has been set successfully!")
        print(f"Provider: {provider.get_name()}")
        print(f"Category: {category}")
        print(f"Saved to: {wallpaper_path}")
        print("=" * 50 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
