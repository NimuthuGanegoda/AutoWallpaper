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

def run_wallpaper_update(provider, category, mood, resolution):
    """
    Downloads and sets the wallpaper.

    Args:
        provider: The provider object
        category: The category string
        mood: The mood string
        resolution: The resolution string
    """
    print("\n" + "=" * 50)
    print("⏳ DOWNLOADING WALLPAPER")
    print("=" * 50)

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
    print(f"Provider: {provider.get_name()}")
    print(f"Category: {category}")
    print(f"Resolution: {resolution}")
    print(f"Saved to: {wallpaper_path}")
    print("=" * 50 + "\n")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper - Download and set wallpapers.")

    parser.add_argument("--provider", type=str, help="Provider name or ID (e.g. '3' or 'waifu.im')")
    parser.add_argument("--category", type=str, help="Category (e.g. 'nature', 'waifu')")
    parser.add_argument("--mood", type=str, default="", help="Mood (e.g. 'dark', 'calm')")
    parser.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION, help="Resolution (e.g. '1920x1080')")
    parser.add_argument("--loop", type=int, help="Run in a loop every X minutes")

    return parser.parse_args()


def get_provider_by_arg(arg):
    """Get provider object from argument string (name or ID)."""
    # Check by ID
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
    args = parse_arguments()

    # Non-interactive mode (arguments provided)
    if args.provider:
        provider = get_provider_by_arg(args.provider)
        if not provider:
            print(f"❌ Error: Provider '{args.provider}' not found.")
            sys.exit(1)

        category = args.category or "random" # Default to random if not specified in CLI

        if args.loop:
            print(f"🔄 Starting wallpaper loop (Every {args.loop} minutes)...")
            try:
                while True:
                    try:
                        run_wallpaper_update(provider, category, args.mood, args.resolution)
                    except Exception as e:
                        print(f"❌ Error in loop: {e}")

                    print(f"💤 Sleeping for {args.loop} minutes...")
                    time.sleep(args.loop * 60)
            except KeyboardInterrupt:
                print("\n🛑 Loop stopped by user.")
                sys.exit(0)
        else:
            try:
                run_wallpaper_update(provider, category, args.mood, args.resolution)
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)

        return

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
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
