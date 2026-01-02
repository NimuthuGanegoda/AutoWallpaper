#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py
    python main.py --help
    python main.py --loop 60 --provider waifu.im --category random
"""

import sys
import argparse
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import PROVIDERS, CATEGORIES, DEFAULT_PROVIDER, DEFAULT_CATEGORY
from ui import (
    get_provider,
    get_category,
    get_mood,
    get_resolution,
)
from wallpaper import save_wallpaper, set_wallpaper


def get_provider_by_name_or_id(name_or_id):
    """Find a provider by name or ID."""
    # Check by ID
    if name_or_id in PROVIDERS:
        return PROVIDERS[name_or_id]

    # Check by name (case insensitive)
    for p in PROVIDERS.values():
        if p.get_name().lower() == name_or_id.lower():
            return p

    return None


def run_wallpaper_update(provider, category, mood, resolution, verbose=False):
    """Run a single wallpaper update."""
    try:
        if verbose:
            print("\n" + "=" * 50)
            print(f"⏳ DOWNLOADING WALLPAPER FROM {provider.get_name()}")
            print("=" * 50)

        # Download image from provider
        image_data = provider.download_image(category, mood)

        # Save the wallpaper
        wallpaper_path = save_wallpaper(image_data)

        if verbose:
            print(f"✅ Saved to: {wallpaper_path}")
            print("\n" + "=" * 50)
            print("🎨 SETTING WALLPAPER")
            print("=" * 50)

        # Set the wallpaper
        set_wallpaper(wallpaper_path)

        if verbose:
            print("\n" + "=" * 50)
            print("✨ SUCCESS!")
            print("=" * 50)
            print(f"Wallpaper updated successfully.")
            print("=" * 50 + "\n")

    except Exception as e:
        print(f"❌ Error updating wallpaper: {e}")


def main():
    """Main entry point for the application."""

    parser = argparse.ArgumentParser(description="Easy Wallpaper - Download and set wallpapers.")
    parser.add_argument("--provider", help="Provider name or ID (e.g., 'waifu.im', '1')")
    parser.add_argument("--category", help="Category to search for")
    parser.add_argument("--mood", help="Mood/filter", default="")
    parser.add_argument("--resolution", help="Target resolution (informational)", default="1920x1080")
    parser.add_argument("--loop", type=int, help="Run in a loop, updating every X minutes")
    parser.add_argument("--list-providers", action="store_true", help="List available providers")

    args = parser.parse_args()

    # Handle listing providers
    if args.list_providers:
        print("Available Providers:")
        for k, p in PROVIDERS.items():
            print(f"{k}. {p.get_name()} - {p.get_description()}")
        sys.exit(0)

    # If no arguments provided, run interactive UI
    if not any([args.provider, args.category, args.loop]):
        run_interactive()
    else:
        run_cli(args)


def run_interactive():
    """Run the interactive UI."""
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
        
        run_wallpaper_update(provider, category, mood, resolution, verbose=True)
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)


def run_cli(args):
    """Run in CLI mode."""

    # Determine provider
    provider = None
    if args.provider:
        provider = get_provider_by_name_or_id(args.provider)
        if not provider:
            print(f"❌ Provider '{args.provider}' not found.")
            sys.exit(1)
    else:
        # Default provider if not specified but other args are present
        provider = PROVIDERS[DEFAULT_PROVIDER]
        print(f"ℹ️  Using default provider: {provider.get_name()}")

    # Determine category
    category = args.category
    if not category:
        # If running in loop, we might want random categories?
        # For now, let's use a default if available or 'random'
        category = "random"
        print(f"ℹ️  Using default category: {category}")

    # Run loop or single shot
    if args.loop:
        print(f"🔄 Starting wallpaper loop. Updating every {args.loop} minutes.")
        print(f"   Provider: {provider.get_name()}")
        print(f"   Category: {category}")
        print(f"   Mood: {args.mood}")

        try:
            while True:
                print(f"\n⏰ Updating wallpaper at {time.strftime('%H:%M:%S')}...")
                run_wallpaper_update(provider, category, args.mood, args.resolution, verbose=True)

                print(f"💤 Sleeping for {args.loop} minutes...")
                time.sleep(args.loop * 60)
        except KeyboardInterrupt:
            print("\n❌ Loop stopped by user.")
            sys.exit(0)
    else:
        run_wallpaper_update(provider, category, args.mood, args.resolution, verbose=True)


if __name__ == "__main__":
    main()
