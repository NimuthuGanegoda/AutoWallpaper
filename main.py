#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe, Wallhaven, Bing, Unsplash, Picsum)
and automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py [options]

Options:
    --provider <name>       Provider name (e.g., 'waifu.im', 'Pexels') or index
    --category <name>       Category to search for
    --mood <name>           Mood filter (if supported)
    --resolution <res>      Resolution (e.g., '1920x1080')
    --loop <minutes>        Run in a loop, updating wallpaper every N minutes
    --help                  Show this help message
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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper Downloader & Setter")

    parser.add_argument("--provider", type=str, help="Provider name or index")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, help="Mood filter")
    parser.add_argument("--resolution", type=str, help="Resolution (e.g. 1920x1080)")
    parser.add_argument("--loop", type=int, help="Update wallpaper every N minutes")
    
    return parser.parse_args()


def get_provider_by_arg(arg: str):
    """Find provider by name or index from argument."""
    # Check if arg is an index
    if arg in PROVIDERS:
        return arg, PROVIDERS[arg]

    # Check if arg is a name (case insensitive)
    arg_lower = arg.lower()
    for key, provider in PROVIDERS.items():
        if provider.get_name().lower() == arg_lower:
            return key, provider

    return None, None


def run_once(provider, category, mood, resolution, interactive=False):
    """Run a single wallpaper update cycle."""
    try:
        print("\n" + "=" * 50)
        print("⏳ DOWNLOADING WALLPAPER")
        print("=" * 50)
        print(f"Provider: {provider.get_name()}")
        print(f"Category: {category}")
        if mood:
            print(f"Mood: {mood}")
        
        # Download image from provider
        # Note: Resolution is not used by all providers, and `download_image` signature
        # doesn't take it (except implicitly for Picsum if we hacked it, but we didn't change the signature)
        # Some providers might benefit from resolution config if we updated them,
        # but for now we follow the existing interface.
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
        print(f"Saved to: {wallpaper_path}")
        print("=" * 50 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ Error during update: {e}\n")
        if interactive:
            # Re-raise if interactive to show full error or exit
            # But main loop catches it.
            pass
        return False


def main():
    """Main entry point for the application."""
    args = parse_args()

    # Header
    print("\n" + "🖼️  " * 12)
    print(" " * 8 + "WELCOME TO EASY WALLPAPER")
    print("🖼️  " * 12)

    # Determine mode
    interactive = True
    if args.provider or args.loop:
        interactive = False

    # Logic for non-interactive / scheduled mode
    if not interactive:
        # Resolve provider
        provider_arg = args.provider or DEFAULT_PROVIDER
        key, provider = get_provider_by_arg(provider_arg)

        if not provider:
            print(f"❌ Error: Invalid provider '{provider_arg}'")
            sys.exit(1)

        category = args.category or DEFAULT_CATEGORY
        mood = args.mood or ""
        resolution = args.resolution or DEFAULT_RESOLUTION

        if args.loop:
            print(f"\n🔄 Running in loop mode. Updating every {args.loop} minutes.")

            while True:
                success = run_once(provider, category, mood, resolution, interactive=False)

                print(f"Waiting {args.loop} minutes for next update...")
                try:
                    time.sleep(args.loop * 60)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    sys.exit(0)
        else:
            # Run once and exit
            success = run_once(provider, category, mood, resolution, interactive=False)
            if not success:
                sys.exit(1)
            sys.exit(0)

    # Interactive Mode
    try:
        print("\nDownload and set beautiful wallpapers effortlessly!")

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

        run_once(provider, category, mood, resolution, interactive=True)
        
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
