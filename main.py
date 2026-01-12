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
from datetime import datetime

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


def run_wallpaper_update(provider, category, mood, resolution, quiet=False):
    """
    Run a single wallpaper update.
    
    Args:
        provider: The provider object.
        category: The category string.
        mood: The mood string.
        resolution: The resolution string.
        quiet: If True, suppress some output.
    """
    if not quiet:
        print("\n" + "=" * 50)
        print("⏳ DOWNLOADING WALLPAPER")
        print("=" * 50)
        print(f"Provider: {provider.get_name()}")
        print(f"Category: {category}")
        if mood:
            print(f"Mood: {mood}")

    try:
        # Download image from provider
        # Note: Resolution is currently not used by all providers directly in download_image
        # but kept for consistency if we extend it later or if providers support it.
        image_data = provider.download_image(category, mood)
        
        # Save the wallpaper
        wallpaper_path = save_wallpaper(image_data)
        
        # Set the wallpaper
        if not quiet:
            print("\n" + "=" * 50)
            print("🎨 SETTING WALLPAPER")
            print("=" * 50)
        
        set_wallpaper(wallpaper_path)
        
        if not quiet:
            print("\n" + "=" * 50)
            print("✨ SUCCESS!")
            print("=" * 50)
            print(f"Your new wallpaper has been set successfully!")
            print(f"Saved to: {wallpaper_path}")
            print("=" * 50 + "\n")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Wallpaper updated successfully ({provider.get_name()}: {category})")

    except Exception as e:
        print(f"\n❌ Error updating wallpaper: {e}")
        # We don't exit here so the loop can continue if running in loop mode


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Easy Wallpaper Downloader & Setter")
    parser.add_argument("--provider", type=str, help="Provider ID or Name (e.g., '1', 'waifu.im')")
    parser.add_argument("--category", type=str, help="Image category")
    parser.add_argument("--mood", type=str, default="", help="Image mood/filter")
    parser.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION, help="Resolution (e.g., 1920x1080)")
    parser.add_argument("--loop", type=int, help="Run in a loop, updating every N minutes")

    args = parser.parse_args()

    # Check if any arguments are passed. If not, run interactive mode.
    # Note: args.mood has a default, so we check if provider or loop is set to decide on non-interactive mode.
    # Actually, if the user just runs `python main.py`, we want interactive.
    # If they run `python main.py --loop 10`, we need defaults for provider/category if not supplied.

    if len(sys.argv) == 1:
        # INTERACTIVE MODE
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

    else:
        # CLI / AUTOMATED MODE

        # Determine Provider
        provider_arg = args.provider
        if not provider_arg:
            if args.loop:
                 # Default to WaifuIm or Random if loop is set but no provider
                 provider_key = DEFAULT_PROVIDER
                 provider = PROVIDERS[provider_key]
                 print(f"ℹ️  No provider specified. Using default: {provider.get_name()}")
            else:
                print("❌ Error: --provider is required in non-interactive mode.")
                sys.exit(1)
        else:
            # Try to find by key
            if provider_arg in PROVIDERS:
                provider = PROVIDERS[provider_arg]
            else:
                # Try to find by name (case-insensitive)
                found = False
                for p in PROVIDERS.values():
                    if p.get_name().lower() == provider_arg.lower():
                        provider = p
                        found = True
                        break
                if not found:
                    print(f"❌ Error: Provider '{provider_arg}' not found.")
                    print("Available providers:")
                    for k, v in PROVIDERS.items():
                        print(f"  {k}: {v.get_name()}")
                    sys.exit(1)

        # Determine Category
        category = args.category
        if not category:
            if provider.get_name() == "Bing":
                category = "daily"
            else:
                # Use a default category for the provider if available, or just generic
                category = DEFAULT_CATEGORY # "waifu"
                print(f"ℹ️  No category specified. Using default: {category}")

        # Mood & Resolution from args or defaults
        mood = args.mood
        resolution = args.resolution

        if args.loop:
            interval = args.loop
            print(f"🔄 Starting wallpaper update loop. Updating every {interval} minutes.")
            print(f"   Provider: {provider.get_name()}, Category: {category}, Mood: {mood}")
            print("   Press Ctrl+C to stop.")

            try:
                while True:
                    run_wallpaper_update(provider, category, mood, resolution, quiet=True)
                    time.sleep(interval * 60)
            except KeyboardInterrupt:
                print("\n🛑 Loop stopped by user.")
                sys.exit(0)
        else:
            # Single run
            run_wallpaper_update(provider, category, mood, resolution)


if __name__ == "__main__":
    main()
