#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers and automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --loop 60
    python main.py --provider 1 --category nature --resolution 1920x1080
"""

import sys
import argparse
import time
import random
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import PROVIDERS, DEFAULT_RESOLUTION
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

    parser.add_argument("--loop", type=int, help="Run in a loop, updating every N minutes")
    parser.add_argument("--provider", type=str, help="Provider ID (1-8)")
    parser.add_argument("--category", type=str, help="Category name")
    parser.add_argument("--mood", type=str, help="Mood filter")
    parser.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION, help="Resolution (e.g., 1920x1080)")

    return parser.parse_args()


def run_wallpaper_update(provider_key=None, category=None, mood=None, resolution=None, interactive=True):
    """
    Run a single wallpaper update.
    
    Args:
        provider_key: Key of the provider to use
        category: Category string
        mood: Mood string
        resolution: Resolution string
        interactive: Whether to use interactive prompts if arguments are missing
    """
    try:
        if interactive:
            print("\n" + "🖼️  " * 12)
            print(" " * 8 + "WELCOME TO EASY WALLPAPER")
            print("🖼️  " * 12)
            print("\nDownload and set beautiful wallpapers effortlessly!")
        
        # 1. Select Provider
        if provider_key and provider_key in PROVIDERS:
            provider = PROVIDERS[provider_key]
            if interactive:
                print(f"✅ Selected provider: {provider.get_name()}")
        elif interactive:
            provider_key, provider = get_provider()
        else:
            # Default to random provider if not specified in non-interactive mode
            provider_key = random.choice(list(PROVIDERS.keys()))
            provider = PROVIDERS[provider_key]
            print(f"🎲 Randomly selected provider: {provider.get_name()}")

        # 2. Select Category
        if not category:
            if interactive:
                category = get_category(provider.get_name())
                print(f"✅ Selected category: {category}")
            else:
                # Default behavior for non-interactive: pick random or specific default
                # But get_category in ui.py asks for input if not found.
                # We need logic here to avoid stuck on input.
                from config import CATEGORIES
                cats = CATEGORIES.get(provider.get_name(), [])
                if cats:
                    category = random.choice(cats)
                elif provider.get_name() == "Bing":
                    category = "daily"
                else:
                    category = "random" # Fallback
                print(f"🎲 Randomly selected category: {category}")

        # 3. Select Mood
        if mood is None:
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

        if interactive:
            print("\n" + "=" * 50)
            print("⏳ DOWNLOADING WALLPAPER")
            print("=" * 50)
        else:
            print(f"⏳ Downloading wallpaper from {provider.get_name()} ({category}, {resolution})...")
        
        # Download image from provider
        # Note: Updated signature requires resolution
        image_data = provider.download_image(category, resolution, mood)
        
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
            print(f"✅ Wallpaper updated successfully! ({wallpaper_path})")

    except Exception as e:
        print(f"❌ Error during update: {e}")
        if interactive:
            # Re-raise to exit in main
            raise e


def main():
    """Main entry point for the application."""
    args = parse_args()

    if args.loop:
        print(f"🔄 Starting wallpaper loop (every {args.loop} minutes)...")
        while True:
            run_wallpaper_update(
                provider_key=args.provider,
                category=args.category,
                mood=args.mood,
                resolution=args.resolution,
                interactive=False
            )
            print(f"💤 Sleeping for {args.loop} minutes...")
            time.sleep(args.loop * 60)

    elif args.provider or args.category:
        # One-shot non-interactive if arguments provided
        run_wallpaper_update(
            provider_key=args.provider,
            category=args.category,
            mood=args.mood,
            resolution=args.resolution,
            interactive=False
        )
    else:
        # Interactive mode
        try:
            run_wallpaper_update(interactive=True)
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            sys.exit(0)
        except Exception:
            sys.exit(1)


if __name__ == "__main__":
    main()
