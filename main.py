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

from config import (
    PROVIDERS,
    DEFAULT_PROVIDER,
    DEFAULT_CATEGORY,
    DEFAULT_RESOLUTION
)
from ui import (
    get_provider,
    get_category,
    get_mood,
    get_resolution,
)
from wallpaper import save_wallpaper, set_wallpaper


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper CLI")
    parser.add_argument("--provider", help="Provider ID (e.g. 1, 2, 3)")
    parser.add_argument("--category", help="Image category/search term")
    parser.add_argument("--mood", help="Image mood/style")
    parser.add_argument("--resolution", help="Target resolution (e.g. 1920x1080)")
    parser.add_argument("--loop", type=int, help="Update interval in minutes")
    return parser.parse_args()


def run_wallpaper_update(provider, category, mood, resolution):
    """
    Execute a single wallpaper update.

    Args:
        provider: Provider instance
        category: Category string
        mood: Mood string
        resolution: Resolution string
    """
    print(f"\n🔄 Running update at {time.strftime('%H:%M:%S')}...")
    print(f"   Provider: {provider.get_name()}")
    print(f"   Category: {category}")
    if mood:
        print(f"   Mood: {mood}")
    print(f"   Resolution: {resolution}")
    
    try:
        # Set resolution if supported
        provider.set_resolution(resolution)
        
        # Download
        image_data = provider.download_image(category, mood)
        
        # Save
        wallpaper_path = save_wallpaper(image_data)
        
        # Set
        set_wallpaper(wallpaper_path)
        
        print("✅ Wallpaper updated successfully!")
        
    except Exception as e:
        print(f"❌ Error during update: {e}")


def main():
    """Main entry point for the application."""
    args = parse_args()

    print("\n" + "🖼️  " * 12)
    print(" " * 8 + "WELCOME TO EASY WALLPAPER")
    print("🖼️  " * 12)

    try:
        # Determine configuration
        if args.provider:
            # Non-interactive / CLI mode configuration
            if args.provider not in PROVIDERS:
                print(f"❌ Invalid provider ID: {args.provider}")
                print(f"Available: {', '.join(sorted(PROVIDERS.keys()))}")
                sys.exit(1)

            provider_key = args.provider
            provider = PROVIDERS[provider_key]

            category = args.category if args.category else DEFAULT_CATEGORY
            mood = args.mood if args.mood else ""
            resolution = args.resolution if args.resolution else DEFAULT_RESOLUTION

        else:
            # Interactive mode
            # Only run interactive selection if we are NOT in a loop with defaults?
            # Actually, if no args provided, we want interactive.
            # If --loop is provided but no provider, we should probably ask interactively once, then loop.

            print("\nDownload and set beautiful wallpapers effortlessly!")

            provider_key, provider = get_provider()
            category = get_category(provider.get_name())
            print(f"✅ Selected category: {category}")

            mood = get_mood(provider.get_name())
            if mood:
                print(f"✅ Selected mood: {mood}")

            resolution = get_resolution()
            print(f"✅ Selected resolution: {resolution}")
        
        
        # Run the update
        run_wallpaper_update(provider, category, mood, resolution)
        
        # Handle loop
        if args.loop:
            interval_seconds = args.loop * 60
            print(f"\n🔄 Scheduled loop enabled. Updating every {args.loop} minutes.")
            print("Press Ctrl+C to stop.")

            while True:
                try:
                    time.sleep(interval_seconds)
                    run_wallpaper_update(provider, category, mood, resolution)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    break
        
        elif not args.provider:
             # Only show success summary if interactive and not looping
             print("\n" + "=" * 50)
             print("✨ SUCCESS!")
             print("=" * 50)
             print(f"Your new wallpaper has been set successfully!")
             print(f"Provider: {provider.get_name()}")
             print("=" * 50 + "\n")

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
