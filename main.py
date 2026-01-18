#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe, etc.) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py [options]

Options:
    --provider <id>     Provider ID (see config.py or run interactive)
    --category <name>   Image category
    --mood <name>       Image mood
    --resolution <res>  Image resolution (e.g. 1920x1080)
    --loop <minutes>    Run in a loop, updating every X minutes
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
    Downloads and sets the wallpaper.

    Args:
        provider: ImageProvider instance
        category: Category string
        mood: Mood string
        resolution: Resolution string
    """
    print("\n" + "=" * 50)
    print(f"⏳ DOWNLOADING WALLPAPER")
    print(f"Provider: {provider.get_name()}")
    print(f"Category: {category}")
    print(f"Mood: {mood}")
    print(f"Resolution: {resolution}")
    print("=" * 50)

    # Download image from provider
    # Note: resolution is passed to support providers that use it (e.g. Picsum, Wallhaven)
    image_data = provider.download_image(category, mood, resolution=resolution)

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


def interactive_mode():
    """Runs the application in interactive CLI mode."""
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


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper CLI")
    parser.add_argument("--provider", help="Provider ID (1-8)")
    parser.add_argument("--category", help="Image category")
    parser.add_argument("--mood", help="Image mood")
    parser.add_argument("--resolution", help="Image resolution (e.g. 1920x1080)")
    parser.add_argument("--loop", type=int, help="Update interval in minutes")

    args = parser.parse_args()

    # Check if any argument is provided (excluding default help/None)
    # If no args are provided, run interactive mode
    if not any([args.provider, args.category, args.mood, args.resolution, args.loop]):
        interactive_mode()
        return

    # Automated / CLI mode
    try:
        provider_id = args.provider or DEFAULT_PROVIDER
        if provider_id not in PROVIDERS:
            print(f"❌ Invalid provider ID: {provider_id}")
            print(f"Available providers: {', '.join(PROVIDERS.keys())}")
            sys.exit(1)

        provider = PROVIDERS[provider_id]
        category = args.category or DEFAULT_CATEGORY
        mood = args.mood or ""
        resolution = args.resolution or DEFAULT_RESOLUTION

        interval = args.loop

        if interval:
            print(f"🔄 Starting loop mode (Interval: {interval} minutes)")
            print(f"Settings: Provider={provider.get_name()}, Category={category}, Mood={mood}, Resolution={resolution}")

            while True:
                try:
                    run_wallpaper_update(provider, category, mood, resolution)
                    print(f"💤 Sleeping for {interval} minutes...")
                    time.sleep(interval * 60)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    sys.exit(0)
                except Exception as e:
                    print(f"❌ Error during update: {e}")
                    print(f"💤 Retrying in {interval} minutes...")
                    time.sleep(interval * 60)
        else:
            # Run once
            run_wallpaper_update(provider, category, mood, resolution)

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
