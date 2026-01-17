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
from config import PROVIDERS, DEFAULT_PROVIDER, DEFAULT_CATEGORY, DEFAULT_RESOLUTION

def run_wallpaper_update(provider_key, provider, category, mood, resolution):
    """Encapsulated logic for downloading and setting wallpaper."""
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
    print(f"Saved to: {wallpaper_path}")
    print("=" * 50 + "\n")

def main():
    """Main entry point for the application."""
    
    parser = argparse.ArgumentParser(description="Easy Wallpaper - Download and set wallpapers.")
    parser.add_argument("--provider", type=str, help="Provider ID (e.g., 1, 2, 3...)")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, help="Mood filter (optional)")
    parser.add_argument("--resolution", type=str, help="Resolution (e.g., 1920x1080)")
    parser.add_argument("--loop", type=int, help="Run in a loop every X minutes")

    args = parser.parse_args()

    # Interactive mode if no arguments or partial arguments (but not loop)
    interactive = not any([args.provider, args.category, args.resolution, args.loop])

    if interactive:
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

            run_wallpaper_update(provider_key, provider, category, mood, resolution)

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
        # Argument processing mode
        provider_key = args.provider or DEFAULT_PROVIDER
        category = args.category or DEFAULT_CATEGORY
        mood = args.mood or ""
        resolution = args.resolution or DEFAULT_RESOLUTION
        
        if provider_key not in PROVIDERS:
            print(f"❌ Error: Invalid provider key '{provider_key}'. Available: {', '.join(PROVIDERS.keys())}")
            sys.exit(1)

        provider = PROVIDERS[provider_key]
        
        print(f"Configuration: Provider={provider.get_name()}, Category={category}, Mood={mood}, Resolution={resolution}")
        
        if args.loop:
            print(f"🔄 Starting loop: Updating every {args.loop} minutes.")
            while True:
                try:
                    run_wallpaper_update(provider_key, provider, category, mood, resolution)
                    print(f"Sleeping for {args.loop} minutes...")
                    time.sleep(args.loop * 60)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    sys.exit(0)
                except Exception as e:
                    print(f"❌ Error in loop: {e}")
                    print(f"Retrying in {args.loop} minutes...")
                    time.sleep(args.loop * 60)
        else:
            try:
                run_wallpaper_update(provider_key, provider, category, mood, resolution)
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()
