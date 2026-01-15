#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --help
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

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


def run_wallpaper_update(provider, category, mood, resolution):
    """
    Core logic to download and set the wallpaper.
    """
    try:
        print("\n" + "=" * 50)
        print(f"⏳ DOWNLOADING WALLPAPER FROM {provider.get_name().upper()}")
        print("=" * 50)
        
        # Download image from provider
        image_data = provider.download_image(category, mood)
        
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
        if mood:
            print(f"Mood: {mood}")
        print(f"Saved to: {wallpaper_path}")
        print("=" * 50 + "\n")
        return True
        
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        return False


def main():
    """Main entry point for the application."""

    parser = argparse.ArgumentParser(description="Easy Wallpaper Downloader & Setter")
    parser.add_argument("--provider", type=str, help="Provider ID (1-8) or name")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, help="Mood filter (optional)", default="")
    parser.add_argument("--resolution", type=str, help="Resolution (e.g., 1920x1080)", default=DEFAULT_RESOLUTION)
    parser.add_argument("--loop", type=int, help="Loop interval in minutes (run continuously)")

    args = parser.parse_args()

    # Non-interactive mode (arguments provided)
    if args.provider or args.loop:

        # Determine provider
        provider_key = args.provider if args.provider else DEFAULT_PROVIDER
        if provider_key in PROVIDERS:
            provider = PROVIDERS[provider_key]
        else:
            # Try to find by name
            found = False
            for k, p in PROVIDERS.items():
                if p.get_name().lower() == provider_key.lower():
                    provider = p
                    found = True
                    break
            if not found:
                 # Default if invalid
                 provider = PROVIDERS[DEFAULT_PROVIDER]
                 print(f"⚠️ Provider '{provider_key}' not found. Using default: {provider.get_name()}")

        category = args.category if args.category else DEFAULT_CATEGORY
        mood = args.mood
        resolution = args.resolution

        if args.loop:
            print(f"🔄 Starting wallpaper loop every {args.loop} minutes...")
            print(f"Provider: {provider.get_name()}, Category: {category}, Mood: {mood}")

            while True:
                print(f"\n⏰ Loop execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                run_wallpaper_update(provider, category, mood, resolution)

                print(f"💤 Sleeping for {args.loop} minutes...")
                try:
                    time.sleep(args.loop * 60)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    break
        else:
            # Single run
            run_wallpaper_update(provider, category, mood, resolution)

    else:
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

            # Run update
            run_wallpaper_update(provider, category, mood, resolution)

        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            sys.exit(0)


if __name__ == "__main__":
    main()
