#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --provider 3 --category "waifu" --loop 60
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import PROVIDERS, DEFAULT_PROVIDER, DEFAULT_CATEGORY, DEFAULT_RESOLUTION
from ui import (
    get_provider,
    get_category,
    get_mood,
    get_resolution,
)
from wallpaper import save_wallpaper, set_wallpaper


def run_wallpaper_update(provider_key, category, mood, resolution):
    """
    Execute the wallpaper update process.

    Args:
        provider_key (str): Key of the provider to use.
        category (str): Category or search term.
        mood (str): Mood filter (optional).
        resolution (str): Desired resolution (e.g., "1920x1080").

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        if provider_key not in PROVIDERS:
            print(f"❌ Invalid provider key: {provider_key}")
            return False

        provider = PROVIDERS[provider_key]
        print(f"\n🔄 Running wallpaper update with provider: {provider.get_name()}")
        print(f"   Category: {category}")
        if mood:
            print(f"   Mood: {mood}")
        print(f"   Resolution: {resolution}")

        # Download image from provider
        image_data = provider.download_image(category, mood, resolution)

        # Save the wallpaper
        wallpaper_path = save_wallpaper(image_data)

        # Set the wallpaper
        print("🎨 Setting wallpaper...")
        set_wallpaper(wallpaper_path)

        print("✨ Wallpaper updated successfully!\n")
        return True

    except Exception as e:
        print(f"❌ Error during update: {e}\n")
        return False


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper Downloader & Setter")
    parser.add_argument("--provider", help="Provider key (see config.py or interactive mode)")
    parser.add_argument("--category", help="Image category or search term")
    parser.add_argument("--mood", help="Mood filter (optional)", default="")
    parser.add_argument("--resolution", help="Resolution (e.g., 1920x1080)", default=DEFAULT_RESOLUTION)
    parser.add_argument("--loop", type=int, help="Loop interval in minutes (run continuously)")

    args = parser.parse_args()

    # Check if running in non-interactive mode (arguments provided)
    if args.provider or args.loop:
        provider_key = args.provider or DEFAULT_PROVIDER
        category = args.category or DEFAULT_CATEGORY
        mood = args.mood
        resolution = args.resolution

        if args.loop:
            print(f"🔁 Starting scheduled loop every {args.loop} minutes...")
            try:
                while True:
                    run_wallpaper_update(provider_key, category, mood, resolution)
                    print(f"💤 Sleeping for {args.loop} minutes...")
                    time.sleep(args.loop * 60)
            except KeyboardInterrupt:
                print("\n🛑 Loop stopped by user.")
                sys.exit(0)
        else:
            # Single run with arguments
            success = run_wallpaper_update(provider_key, category, mood, resolution)
            sys.exit(0 if success else 1)

    # Interactive mode
    print("\n" + "🖼️  " * 12)
    print(" " * 8 + "WELCOME TO EASY WALLPAPER")
    print("🖼️  " * 12)
    print("\nDownload and set beautiful wallpapers effortlessly!")
    
    try:
        # Get provider selection
        provider_key, provider = get_provider()
        
        # Get category
        category = get_category(provider.get_name())
        print(f"✅ Selected category: {category}")
        
        # Get mood (if available)
        mood = get_mood(provider.get_name())
        if mood:
            print(f"✅ Selected mood: {mood}")
        
        # Get resolution preference
        resolution = get_resolution()
        print(f"✅ Selected resolution: {resolution}")
        
        # Run the update
        success = run_wallpaper_update(provider_key, category, mood, resolution)
        
        if not success:
            sys.exit(1)
        
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
