#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe, etc.) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --provider 1 --category nature --loop 60
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import PROVIDERS
from ui import (
    get_provider,
    get_category,
    get_mood,
    get_resolution,
)
from wallpaper import save_wallpaper, set_wallpaper


def update_wallpaper(provider, category, mood, resolution):
    """
    Download and set a new wallpaper.

    Args:
        provider: Provider object
        category: Category string
        mood: Mood string
        resolution: Resolution string (unused for now but good for future)
    """
    print("\n" + "=" * 50)
    print("⏳ DOWNLOADING WALLPAPER")
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
    print(f"Saved to: {wallpaper_path}")
    print("=" * 50 + "\n")


def get_provider_by_arg(arg):
    """Get provider from argument (index or name)."""
    # Check by index
    if arg in PROVIDERS:
        return PROVIDERS[arg]

    # Check by name (case insensitive)
    arg_lower = arg.lower()
    for p in PROVIDERS.values():
        if p.get_name().lower() == arg_lower:
            return p

    return None


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper - Download and set wallpapers.")
    parser.add_argument("--provider", help="Provider index (1-8) or name")
    parser.add_argument("--category", help="Image category (e.g., nature, anime)")
    parser.add_argument("--mood", help="Image mood (optional)")
    parser.add_argument("--resolution", help="Resolution (optional, default 1920x1080)")
    parser.add_argument("--loop", type=int, help="Update wallpaper every N minutes")

    args = parser.parse_args()

    print("\n" + "🖼️  " * 12)
    print(" " * 8 + "WELCOME TO EASY WALLPAPER")
    print("🖼️  " * 12)
    print("\nDownload and set beautiful wallpapers effortlessly!")

    try:
        if args.provider:
            # Non-interactive mode
            provider = get_provider_by_arg(args.provider)
            if not provider:
                print(f"❌ Error: Invalid provider '{args.provider}'")
                sys.exit(1)

            category = args.category or "random"
            mood = args.mood or ""
            resolution = args.resolution or "1920x1080"

            print(f"✅ Selected provider: {provider.get_name()}")
            print(f"✅ Selected category: {category}")

            if args.loop:
                print(f"🔄 Loop enabled: Updating every {args.loop} minutes.")
                while True:
                    try:
                        update_wallpaper(provider, category, mood, resolution)
                        print(f"💤 Sleeping for {args.loop} minutes...")
                        time.sleep(args.loop * 60)
                    except Exception as e:
                        print(f"❌ Error in loop: {e}")
                        print("Retrying in 1 minute...")
                        time.sleep(60)
            else:
                update_wallpaper(provider, category, mood, resolution)

        else:
            # Interactive mode
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

            # Interactive loop confirmation?
            # For now, interactive mode just runs once as per original design,
            # unless we add a question "Do you want to loop this?".
            # Let's keep it simple and just run once for interactive.

            update_wallpaper(provider, category, mood, resolution)
        
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
