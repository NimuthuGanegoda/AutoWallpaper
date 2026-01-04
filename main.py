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
import time
import datetime
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
from config import PROVIDERS, DEFAULT_PROVIDER, DEFAULT_CATEGORY, DEFAULT_RESOLUTION


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper - Download and set wallpapers.")
    parser.add_argument("--provider", type=str, help="Provider ID (1-8) or name (e.g. 'Pexels')")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, help="Image mood", default="")
    parser.add_argument("--resolution", type=str, help="Screen resolution (e.g. 1920x1080)")
    parser.add_argument("--loop", type=int, help="Update wallpaper every N minutes (loops forever)")
    return parser.parse_args()


def get_provider_by_arg(arg: str):
    """Get provider instance from argument (ID or name)."""
    if arg in PROVIDERS:
        return PROVIDERS[arg]

    # Try by name (case insensitive)
    arg_lower = arg.lower()
    for p in PROVIDERS.values():
        if p.get_name().lower() == arg_lower:
            return p
    return None


def run_once(provider, category, mood):
    """Run a single wallpaper update cycle."""
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting update...")
    
    try:
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
        return True

    except Exception as e:
        print(f"\n❌ Error during update: {e}\n")
        return False


def main():
    """Main entry point for the application."""
    args = parse_arguments()

    # Check if we should run in non-interactive mode
    is_interactive = not (args.provider or args.category or args.loop)

    if is_interactive:
        print("\n" + "🖼️  " * 12)
        print(" " * 8 + "WELCOME TO EASY WALLPAPER")
        print("🖼️  " * 12)
        print("\nDownload and set beautiful wallpapers effortlessly!")

    try:
        provider = None
        category = None
        mood = ""
        resolution = DEFAULT_RESOLUTION

        if args.provider:
            provider = get_provider_by_arg(args.provider)
            if not provider:
                print(f"❌ Error: Provider '{args.provider}' not found.")
                sys.exit(1)
            print(f"✅ Selected provider: {provider.get_name()}")
        elif is_interactive:
            _, provider = get_provider()
        else:
             # Default provider for loop if not specified? Or should we error?
             # Let's use default from config
             provider = PROVIDERS[DEFAULT_PROVIDER]
             print(f"ℹ️ Using default provider: {provider.get_name()}")

        if args.category:
            category = args.category
            print(f"✅ Selected category: {category}")
        elif is_interactive:
            category = get_category(provider.get_name())
            print(f"✅ Selected category: {category}")
        else:
             category = DEFAULT_CATEGORY
             print(f"ℹ️ Using default category: {category}")

        if args.mood:
            mood = args.mood
            print(f"✅ Selected mood: {mood}")
        elif is_interactive:
            mood = get_mood(provider.get_name())
            if mood:
                print(f"✅ Selected mood: {mood}")

        if args.resolution:
            resolution = args.resolution
            print(f"✅ Selected resolution: {resolution}")
        elif is_interactive:
            resolution = get_resolution()
            print(f"✅ Selected resolution: {resolution}")

        # Run once or loop
        if args.loop:
            interval_minutes = args.loop
            print(f"🔁 Loop mode enabled. Updating every {interval_minutes} minutes.")

            while True:
                run_once(provider, category, mood)
                print(f"💤 Sleeping for {interval_minutes} minutes...")
                try:
                    time.sleep(interval_minutes * 60)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    break
        else:
            run_once(provider, category, mood)
        
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
