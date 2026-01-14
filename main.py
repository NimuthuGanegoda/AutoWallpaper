#!/usr/bin/env python3
"""
Easy Wallpaper - Download and set wallpapers from various sources.

A modular Python application that allows users to download wallpapers
from multiple providers (Pexels, Pixabay, waifu.im, nekos.moe, etc.) and
automatically set them on Windows, macOS, or Linux.

Usage:
    python main.py                              # Interactive mode
    python main.py --provider 1 --category nature  # One-off mode
    python main.py --provider 3 --loop 30       # Schedule mode
"""

import sys
import time
import argparse
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


def run_wallpaper_update(provider, category, mood, resolution, verbose=True):
    """
    Downloads and sets the wallpaper.

    Args:
        provider: The provider object
        category: Image category
        mood: Image mood
        resolution: Target resolution
        verbose: Whether to print status messages
    """
    if verbose:
        print("\n" + "=" * 50)
        print(f"⏳ DOWNLOADING WALLPAPER FROM {provider.get_name().upper()}")
        print("=" * 50)

    # Download image from provider
    # Note: resolution argument isn't currently used by download_image but could be in future
    image_data = provider.download_image(category, mood)

    # Save the wallpaper
    wallpaper_path = save_wallpaper(image_data)

    # Set the wallpaper
    if verbose:
        print("\n" + "=" * 50)
        print("🎨 SETTING WALLPAPER")
        print("=" * 50)

    set_wallpaper(wallpaper_path)

    if verbose:
        print("\n" + "=" * 50)
        print("✨ SUCCESS!")
        print("=" * 50)
        print(f"Your new wallpaper has been set successfully!")
        print(f"Provider: {provider.get_name()}")
        print(f"Category: {category}")
        print(f"Saved to: {wallpaper_path}")
        print("=" * 50 + "\n")


def resolve_provider(provider_arg):
    """Find provider by ID or name."""
    if provider_arg in PROVIDERS:
        return PROVIDERS[provider_arg]

    for p in PROVIDERS.values():
        if p.get_name().lower() == provider_arg.lower():
            return p
    return None


def interactive_mode():
    """Run in interactive mode."""
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


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper CLI")
    parser.add_argument("--provider", help="Provider ID or Name")
    parser.add_argument("--category", help="Category")
    parser.add_argument("--mood", help="Mood", default="")
    parser.add_argument("--resolution", help="Resolution", default=DEFAULT_RESOLUTION)
    parser.add_argument("--loop", type=int, help="Update interval in minutes")

    args = parser.parse_args()

    # If no arguments provided (other than script name), run interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
        return

    # CLI Mode
    try:
        provider_arg = args.provider or DEFAULT_PROVIDER
        provider = resolve_provider(provider_arg)

        if not provider:
            print(f"❌ Provider '{provider_arg}' not found.")
            print("Available providers:")
            for k, p in PROVIDERS.items():
                print(f"  {k}: {p.get_name()}")
            sys.exit(1)

        category = args.category or DEFAULT_CATEGORY
        mood = args.mood
        resolution = args.resolution

        if args.loop:
            print(f"🔄 Starting wallpaper loop. Updating every {args.loop} minutes.")
            print(f"Provider: {provider.get_name()}")
            print(f"Category: {category}")
            print(f"Mood: {mood}")

            while True:
                try:
                    print(f"\n[Running update at {time.strftime('%H:%M:%S')}]")
                    run_wallpaper_update(provider, category, mood, resolution, verbose=True)
                    print(f"😴 Sleeping for {args.loop} minutes...")
                    time.sleep(args.loop * 60)
                except KeyboardInterrupt:
                    print("\n🛑 Loop stopped by user.")
                    break
                except Exception as e:
                    print(f"❌ Error in loop: {e}")
                    print("Retrying in 1 minute...")
                    time.sleep(60)
        else:
            run_wallpaper_update(provider, category, mood, resolution, verbose=True)

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
