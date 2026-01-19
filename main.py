#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe, etc.) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py [interactive mode]
    python main.py --provider 1 --category nature --loop 60
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import PROVIDERS, DEFAULT_PROVIDER, DEFAULT_CATEGORY, DEFAULT_RESOLUTION, CATEGORIES
from ui import (
    get_provider,
    get_category,
    get_mood,
    get_resolution,
)
from wallpaper import save_wallpaper, set_wallpaper


def run_wallpaper_update(provider, category, mood, resolution):
    """
    Execute the wallpaper update process.

    Args:
        provider: ImageProvider instance
        category: Category string
        mood: Mood string
        resolution: Resolution string
    """
    print("\n" + "=" * 50)
    print("⏳ STARTING WALLPAPER UPDATE")
    print("=" * 50)
    print(f"Provider:   {provider.get_name()}")
    print(f"Category:   {category}")
    if mood:
        print(f"Mood:       {mood}")
    print(f"Resolution: {resolution}")

    # Special handling for providers that need resolution (Picsum)
    if hasattr(provider, 'set_resolution'):
        provider.set_resolution(resolution)
    
    try:
        # Download image from provider
        print(f"\n⏳ Downloading image...")
        image_data = provider.download_image(category, mood)
        
        # Save the wallpaper
        print(f"💾 Saving wallpaper...")
        wallpaper_path = save_wallpaper(image_data)
        
        # Set the wallpaper
        print(f"🎨 Setting wallpaper...")
        set_wallpaper(wallpaper_path)
        
        print("\n" + "=" * 50)
        print("✨ SUCCESS!")
        print("=" * 50)
        print(f"Wallpaper updated successfully at {time.strftime('%H:%M:%S')}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        # In loop mode, we might want to log error but not crash
        raise e


def get_provider_by_id_or_name(identifier):
    """Get provider instance by ID or name."""
    # Try ID first
    if identifier in PROVIDERS:
        return PROVIDERS[identifier]

    # Try name (case insensitive)
    for p in PROVIDERS.values():
        if p.get_name().lower() == identifier.lower():
            return p

    return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper - Auto Wallpaper Changer")
    parser.add_argument("-p", "--provider", help="Provider ID or Name (e.g. '1' or 'waifu.im')")
    parser.add_argument("-c", "--category", help="Image category")
    parser.add_argument("-m", "--mood", help="Image mood/style")
    parser.add_argument("-r", "--resolution", help="Resolution (e.g. 1920x1080)", default=DEFAULT_RESOLUTION)
    parser.add_argument("-l", "--loop", type=int, help="Loop interval in minutes")

    args = parser.parse_args()

    # Check if we should run in interactive mode
    # If no provider is specified and no loop, assume interactive
    if not args.provider and not args.loop and not args.category:
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

            run_wallpaper_update(provider, category, mood, resolution)

        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            sys.exit(1)

    else:
        # CLI / Scheduled mode

        # Determine provider
        provider_id = args.provider if args.provider else DEFAULT_PROVIDER
        provider = get_provider_by_id_or_name(provider_id)

        if not provider:
            print(f"❌ Error: Provider '{provider_id}' not found.")
            print("Available providers:")
            for k, v in PROVIDERS.items():
                print(f"  {k}: {v.get_name()}")
            sys.exit(1)

        # Determine category
        category = args.category
        if not category:
            # Try to pick a default category for the provider
            provider_name = provider.get_name()
            if provider_name in CATEGORIES and CATEGORIES[provider_name]:
                category = CATEGORIES[provider_name][0]
            else:
                category = DEFAULT_CATEGORY

        mood = args.mood if args.mood else ""
        resolution = args.resolution

        if args.loop:
            print(f"🔄 Starting loop mode. Updating every {args.loop} minutes.")
            while True:
                try:
                    run_wallpaper_update(provider, category, mood, resolution)
                except Exception as e:
                    print(f"⚠️ Update failed, retrying next cycle. Error: {e}")

                print(f"💤 Sleeping for {args.loop} minutes...")
                try:
                    time.sleep(args.loop * 60)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    break
        else:
            # Single run
            run_wallpaper_update(provider, category, mood, resolution)


if __name__ == "__main__":
    main()
