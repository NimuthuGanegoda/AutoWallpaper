#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe, etc.) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py                  # Interactive mode
    python main.py --help           # Show CLI options
    python main.py --loop 60        # Update every 60 mins
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


def run_wallpaper_update(provider_key: str, category: str, mood: str, resolution: str) -> None:
    """
    Download and set wallpaper based on parameters.

    Args:
        provider_key: Key of the provider in PROVIDERS dict
        category: Image category
        mood: Image mood
        resolution: Target resolution (mostly for logging/future use as providers handle this differently)
    """
    if provider_key not in PROVIDERS:
        raise RuntimeError(f"Invalid provider key: {provider_key}")

    provider = PROVIDERS[provider_key]

    print(f"\n🚀 Running update with provider: {provider.get_name()}")
    print(f"   Category: {category}, Mood: {mood}, Resolution: {resolution}")
    
    try:
        # Download image from provider
        image_data = provider.download_image(category, mood)
        
        # Save the wallpaper
        wallpaper_path = save_wallpaper(image_data)
        
        # Set the wallpaper
        print("🎨 Setting wallpaper...")
        set_wallpaper(wallpaper_path)
        
        print(f"✨ Wallpaper set successfully! (Source: {provider.get_name()})")
        
    except Exception as e:
        print(f"❌ Error updating wallpaper: {e}")
        raise


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper CLI")

    parser.add_argument(
        "--provider",
        help="Provider key (e.g., 1=Pexels, 3=waifu.im, 5=Wallhaven)",
        default=None
    )
    parser.add_argument(
        "--category",
        help="Image category",
        default=None
    )
    parser.add_argument(
        "--mood",
        help="Image mood",
        default=""
    )
    parser.add_argument(
        "--resolution",
        help="Target resolution (e.g., 1920x1080)",
        default=DEFAULT_RESOLUTION
    )
    parser.add_argument(
        "--loop",
        type=int,
        help="Run in a loop, updating every X minutes",
        default=None
    )

    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()

    # If arguments are provided (other than defaults), or loop is requested, run in CLI mode
    # However, since defaults are None for some, we check if they are set.
    # Actually, if any arg is provided, we skip interactive mode.
    # But argparse sets defaults.

    # A simple heuristic: if sys.argv has arguments > 1, assume CLI mode
    is_cli_mode = len(sys.argv) > 1

    if is_cli_mode:
        print("\n" + "🤖 " * 12)
        print(" " * 8 + "EASY WALLPAPER CLI")
        print("🤖 " * 12 + "\n")

        provider_key = args.provider or DEFAULT_PROVIDER
        category = args.category or DEFAULT_CATEGORY
        mood = args.mood
        resolution = args.resolution

        if args.loop:
            print(f"🔄 Starting wallpaper loop. Updating every {args.loop} minutes.")
            print("Press Ctrl+C to stop.\n")

            try:
                while True:
                    try:
                        run_wallpaper_update(provider_key, category, mood, resolution)
                    except Exception as e:
                        print(f"⚠️ Update failed, retrying next cycle. Error: {e}")

                    print(f"⏳ Sleeping for {args.loop} minutes...")
                    time.sleep(args.loop * 60)
            except KeyboardInterrupt:
                print("\n🛑 Loop stopped by user.")
                sys.exit(0)
        else:
            # Single run
            try:
                run_wallpaper_update(provider_key, category, mood, resolution)
            except Exception:
                sys.exit(1)

    else:
        # Interactive Mode
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

            print("\n" + "=" * 50)
            print("⏳ DOWNLOADING WALLPAPER")
            print("=" * 50)

            # Use the shared function
            run_wallpaper_update(provider_key, category, mood, resolution)

            print("\n" + "=" * 50)
            print("✨ SUCCESS!")
            print("=" * 50)

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
