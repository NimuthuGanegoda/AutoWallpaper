#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --loop 60
    python main.py --provider 3 --category waifu --resolution 1920x1080 --loop 30
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


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper Downloader & Setter")

    parser.add_argument("--loop", type=int, help="Run in a loop every X minutes")
    parser.add_argument("--provider", type=str, help="Provider ID (1-8)")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, help="Mood filter", default="")
    parser.add_argument("--resolution", type=str, help="Resolution (e.g., 1920x1080)")

    return parser.parse_args()


def run_wallpaper_update(provider, category, mood, resolution):
    """
    Execute a single wallpaper update.
    
    Args:
        provider: Provider object
        category: Category string
        mood: Mood string
        resolution: Resolution string
    """
    try:
        print("\n" + "=" * 50)
        print("⏳ DOWNLOADING WALLPAPER")
        print("=" * 50)
        print(f"Provider: {provider.get_name()}")
        print(f"Category: {category}")
        if mood:
            print(f"Mood: {mood}")
        print(f"Resolution: {resolution}")
        
        # Download image from provider
        image_data = provider.download_image(category, mood, resolution)
        
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
        print(f"Saved to: {wallpaper_path}")
        print("=" * 50 + "\n")
        
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")


def main():
    """Main entry point for the application."""
    args = parse_arguments()

    # Interactive mode if no arguments provided (or incomplete set for automation)
    # However, if loop is provided, we need defaults if others are missing?
    # Let's say: if loop is provided, or specific args are provided, we skip interactive.

    interactive = True
    if args.loop or args.provider or args.category:
        interactive = False

    if interactive:
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

            run_wallpaper_update(provider, category, mood, resolution)

        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            sys.exit(0)

    else:
        # Automated / Loop mode
        # Determine configuration

        # Provider
        provider_key = args.provider if args.provider else DEFAULT_PROVIDER
        if provider_key not in PROVIDERS:
            print(f"⚠️ Provider '{provider_key}' not found. Using default ({DEFAULT_PROVIDER}).")
            provider_key = DEFAULT_PROVIDER
        provider = PROVIDERS[provider_key]

        # Category
        category = args.category if args.category else DEFAULT_CATEGORY

        # Mood
        mood = args.mood

        # Resolution
        resolution = args.resolution if args.resolution else DEFAULT_RESOLUTION

        if args.loop:
            interval_minutes = args.loop
            print(f"🔄 Starting wallpaper loop (Every {interval_minutes} minutes)")
            print("Press Ctrl+C to stop.")

            try:
                while True:
                    run_wallpaper_update(provider, category, mood, resolution)

                    print(f"💤 Sleeping for {interval_minutes} minutes...")
                    time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\n🛑 Loop stopped by user.")
                sys.exit(0)
        else:
            # Just run once with provided args
            run_wallpaper_update(provider, category, mood, resolution)


if __name__ == "__main__":
    main()
