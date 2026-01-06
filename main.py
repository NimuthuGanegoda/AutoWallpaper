#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --provider 1 --category nature --loop 60
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
    parser = argparse.ArgumentParser(description="Download and set wallpapers.")
    parser.add_argument("--provider", type=str, help="Provider ID (1-8)")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, default="", help="Image mood (optional)")
    parser.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION, help="Wallpaper resolution")
    parser.add_argument("--loop", type=int, help="Loop interval in minutes (optional)")
    return parser.parse_args()

def run_wallpaper_update(provider, category, mood, resolution, interactive=True):
    """Run a single wallpaper update."""
    if interactive:
        print("\n" + "=" * 50)
        print("⏳ DOWNLOADING WALLPAPER")
        print("=" * 50)
    else:
        print(f"⏳ Downloading wallpaper from {provider.get_name()} ({category})...")

    # Download image from provider
    image_data = provider.download_image(category, mood)

    # Save the wallpaper
    wallpaper_path = save_wallpaper(image_data)

    # Set the wallpaper
    if interactive:
        print("\n" + "=" * 50)
        print("🎨 SETTING WALLPAPER")
        print("=" * 50)

    set_wallpaper(wallpaper_path)

    if interactive:
        print("\n" + "=" * 50)
        print("✨ SUCCESS!")
        print("=" * 50)
        print(f"Your new wallpaper has been set successfully!")
        print(f"Provider: {provider.get_name()}")
        print(f"Category: {category}")
        print(f"Saved to: {wallpaper_path}")
        print("=" * 50 + "\n")
    else:
        print(f"✅ Wallpaper set successfully! ({wallpaper_path})")

def main():
    """Main entry point for the application."""
    args = parse_args()

    # Interactive mode (no args provided)
    if not any([args.provider, args.category, args.loop]):
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

            run_wallpaper_update(provider, category, mood, resolution, interactive=True)

        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            sys.exit(0)
        except RuntimeError as e:
            print(f"\n❌ Error: {e}\n")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")
            sys.exit(1)

    else:
        # CLI / Loop mode
        if not args.provider or not args.category:
            print("❌ Error: --provider and --category are required for non-interactive mode.")
            sys.exit(1)

        provider_key = args.provider
        if provider_key not in PROVIDERS:
            print(f"❌ Error: Invalid provider ID '{provider_key}'. Available: {list(PROVIDERS.keys())}")
            sys.exit(1)

        provider = PROVIDERS[provider_key]
        category = args.category
        mood = args.mood
        resolution = args.resolution

        try:
            if args.loop:
                print(f"🔄 Starting loop mode. Updating wallpaper every {args.loop} minutes.")
                print(f"Provider: {provider.get_name()}, Category: {category}")

                while True:
                    try:
                        run_wallpaper_update(provider, category, mood, resolution, interactive=False)
                    except Exception as e:
                        print(f"⚠️ Error updating wallpaper: {e}")

                    print(f"😴 Sleeping for {args.loop} minutes...")
                    time.sleep(args.loop * 60)
            else:
                run_wallpaper_update(provider, category, mood, resolution, interactive=False)

        except KeyboardInterrupt:
            print("\n🛑 Loop stopped by user.")
            sys.exit(0)

if __name__ == "__main__":
    main()
