#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers and automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --loop 60
    python main.py --provider 1 --category nature --loop 30
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


def run_wallpaper_update(provider, category, mood, resolution):
    """
    Executes a single wallpaper update cycle.

    Args:
        provider: The provider object
        category: Image category
        mood: Image mood
        resolution: Image resolution
    """
    print(f"\n--- Starting Wallpaper Update: {provider.get_name()} ({category}) ---")
    
    try:
        print("⏳ Downloading wallpaper...")
        image_data = provider.download_image(category, mood, resolution)
        
        print("💾 Saving wallpaper...")
        wallpaper_path = save_wallpaper(image_data)
        
        print("🎨 Setting wallpaper...")
        set_wallpaper(wallpaper_path)
        
        print(f"✨ Success! Wallpaper set to: {wallpaper_path}")
        return True

    except Exception as e:
        print(f"❌ Error updating wallpaper: {e}")
        return False


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper Auto Changer")
    parser.add_argument("--loop", type=int, help="Run in a loop, updating every N minutes")
    parser.add_argument("--provider", type=str, help="Provider ID (1-8)")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, help="Image mood", default="")
    parser.add_argument("--resolution", type=str, help="Resolution (e.g. 1920x1080)", default=DEFAULT_RESOLUTION)

    args = parser.parse_args()

    # If arguments are provided, use them. Otherwise, use interactive mode.
    # However, if loop is requested but no provider is specified, we might default or ask.
    # If no args are provided at all, go to interactive mode.

    # Check if we should run in non-interactive CLI mode
    is_cli_mode = args.loop or args.provider or args.category

    if is_cli_mode:
        print("🚀 Running in CLI Mode")
        
        # Determine provider
        provider_key = args.provider if args.provider else DEFAULT_PROVIDER
        if provider_key not in PROVIDERS:
            print(f"❌ Invalid provider key '{provider_key}'. Using default ({DEFAULT_PROVIDER}).")
            provider_key = DEFAULT_PROVIDER
        
        provider = PROVIDERS[provider_key]
        
        # Determine category
        category = args.category if args.category else DEFAULT_CATEGORY
        
        # Determine mood and resolution
        mood = args.mood
        resolution = args.resolution
        
        print(f"Configuration: Provider={provider.get_name()}, Category={category}, Mood={mood}, Resolution={resolution}")
        
        if args.loop:
            interval_minutes = args.loop
            print(f"🔄 Loop enabled. Updating every {interval_minutes} minutes.")
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
            # Single run
            run_wallpaper_update(provider, category, mood, resolution)

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

            # Run the update
            if run_wallpaper_update(provider, category, mood, resolution):
                print("=" * 50)
                print("✨ SUCCESS!")
                print("=" * 50)
                print(f"Your new wallpaper has been set successfully!")
                print(f"Provider: {provider.get_name()}")
                print(f"Category: {category}")
            else:
                print("❌ Failed to set wallpaper.")

        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
