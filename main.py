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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui import (
    get_provider,
    get_category,
    get_mood,
    get_resolution,
)
from wallpaper import save_wallpaper, set_wallpaper
from config import PROVIDERS, DEFAULT_RESOLUTION

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Download and set wallpapers from various sources.")

    parser.add_argument("--provider", type=str, help="Provider ID or Name (e.g., '1' or 'Pexels')")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, help="Image mood/style")
    parser.add_argument("--resolution", type=str, help="Target resolution (e.g., 1920x1080)")
    parser.add_argument("--loop", type=int, help="Loop interval in minutes (run continuously)")

    return parser.parse_args()

def run_wallpaper_update(provider_key=None, category=None, mood=None, resolution=None, interactive=True):
    """
    Run a single wallpaper update.

    Args:
        provider_key: Key of the provider to use (optional)
        category: Category string (optional)
        mood: Mood string (optional)
        resolution: Resolution string (optional)
        interactive: Whether to prompt user for missing info
    """
    
    try:
        provider = None
        
        # 1. Select Provider
        if provider_key:
            if provider_key in PROVIDERS:
                provider = PROVIDERS[provider_key]
            else:
                # Try to find by name
                for k, p in PROVIDERS.items():
                    if p.get_name().lower() == provider_key.lower():
                        provider = p
                        provider_key = k
                        break
        
        if not provider:
            if interactive:
                provider_key, provider = get_provider()
            else:
                print("❌ No provider specified. Use --provider or run interactively.")
                return False

        # 2. Select Category
        if not category:
            if interactive:
                category = get_category(provider.get_name())
                print(f"✅ Selected category: {category}")
            else:
                # Default behavior if not specified in non-interactive: "random" or provider specific default
                # But for now, let's just pick 'random' or fail?
                # Better to default to 'random' or the first available category if safe.
                # 'waifu' is safe for waifu.im. 'random' is good for Unsplash.
                category = "random"
                print(f"⚠️  No category specified, using default: {category}")

        # 3. Select Mood
        if mood is None: # explicit None means check args
            if interactive:
                mood = get_mood(provider.get_name())
                if mood:
                    print(f"✅ Selected mood: {mood}")
            else:
                mood = "" # Default to no mood
        
        # 4. Select Resolution
        if not resolution:
            if interactive:
                resolution = get_resolution()
                print(f"✅ Selected resolution: {resolution}")
            else:
                resolution = DEFAULT_RESOLUTION
                print(f"⚠️  No resolution specified, using default: {resolution}")
        
        # Set resolution on provider
        provider.set_resolution(resolution)

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
        
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        return False

def main():
    """Main entry point for the application."""
    args = parse_args()

    # Check if any arguments are provided to determine mode
    has_args = any([args.provider, args.category, args.mood, args.resolution, args.loop])

    print("\n" + "🖼️  " * 12)
    print(" " * 8 + "WELCOME TO EASY WALLPAPER")
    print("🖼️  " * 12)
    print("\nDownload and set beautiful wallpapers effortlessly!")

    try:
        if args.loop:
            print(f"🔄 Starting loop mode (Interval: {args.loop} minutes)")
            while True:
                success = run_wallpaper_update(
                    provider_key=args.provider,
                    category=args.category,
                    mood=args.mood,
                    resolution=args.resolution,
                    interactive=False
                )

                if not success:
                    print("⚠️ Update failed, retrying in next interval...")

                print(f"💤 Sleeping for {args.loop} minutes...")
                time.sleep(args.loop * 60)
        else:
            # Single run
            run_wallpaper_update(
                provider_key=args.provider,
                category=args.category,
                mood=args.mood,
                resolution=args.resolution,
                interactive=not has_args
            )

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
