"""
User interface and interaction functions for easy-wallpaper.

Handles all user prompts and menu displays.
"""

from config import PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS


def get_nsfw_preference() -> bool:
    """
    Ask the user if they want to allow NSFW content.

    Returns:
        bool: True if allowed, False otherwise
    """
    print("\n" + "=" * 50)
    print("🔞 NSFW CONTENT SETTING")
    print("=" * 50)
    while True:
        choice = input("Allow NSFW content? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            print("✅ NSFW content allowed")
            return True
        elif choice in ['n', 'no']:
            print("❌ NSFW content disabled")
            return False
        print("❌ Invalid choice. Please enter 'y' or 'n'.")


def get_provider() -> tuple:
    """
    Display provider options and get user selection.
    
    Returns:
        tuple: (provider_key, provider_object)
    """
    print("\n" + "=" * 50)
    print("📱 SELECT IMAGE PROVIDER")
    print("=" * 50)
    print("1. Pexels      - High-quality photos (200 req/hour)")
    print("2. Pixabay     - Diverse images (100 req/hour, API key required)")
    print("3. waifu.im    - Anime waifu (unlimited)")
    print("4. nekos.moe   - Catgirls (unlimited)")
    print("-" * 50)
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        if choice in PROVIDERS:
            provider = PROVIDERS[choice]
            print(f"✅ Selected: {provider.get_name()}")
            return choice, provider
        print("❌ Invalid choice. Please enter 1-4.")


def get_os_choice() -> str:
    """
    Get OS choice for wallpaper selection (used for some providers).
    
    Returns:
        str: OS choice ('windows', 'macos', 'linux', or empty string)
    """
    print("\n" + "=" * 50)
    print("🖥️  OPERATING SYSTEM (Optional)")
    print("=" * 50)
    print("This helps narrow down image results.")
    print("1. Windows")
    print("2. macOS")
    print("3. Linux")
    print("4. No preference")
    print("-" * 50)
    
    choices = {
        "1": "windows",
        "2": "macos",
        "3": "linux",
        "4": "",
    }
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        if choice in choices:
            return choices[choice]
        print("❌ Invalid choice. Please enter 1-4.")


def get_waifu_category(nsfw_allowed: bool) -> str:
    """
    Get waifu category selection.
    
    Args:
        nsfw_allowed: Whether NSFW content is allowed

    Returns:
        str: Selected category
    """
    categories = CATEGORIES.get("waifu.im", [])
    
    print("\n" + "=" * 50)
    print("👩 SELECT WAIFU CATEGORY")
    print("=" * 50)
    
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat.capitalize()}")
    print(f"{len(categories) + 1}. Random")
    print("-" * 50)
    
    while True:
        choice = input(f"Enter your choice (1-{len(categories) + 1}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return categories[idx]
            elif idx == len(categories):
                return "random"
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(categories) + 1}.")
        except ValueError:
            print(f"❌ Please enter a number between 1-{len(categories) + 1}.")


def get_catgirl_category(nsfw_allowed: bool) -> str:
    """
    Get catgirl category selection.
    
    Args:
        nsfw_allowed: Whether NSFW content is allowed

    Returns:
        str: Selected category
    """
    all_categories = CATEGORIES.get("nekos.moe", [])
    categories = []

    # Filter categories based on NSFW setting
    for cat in all_categories:
        if not nsfw_allowed and (cat == "nsfw" or cat == "mixed"):
            continue
        categories.append(cat)
    
    print("\n" + "=" * 50)
    print("🐱 SELECT CATGIRL CATEGORY")
    print("=" * 50)
    
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat.capitalize()}")
    print(f"{len(categories) + 1}. Random")
    print("-" * 50)
    
    while True:
        choice = input(f"Enter your choice (1-{len(categories) + 1}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return categories[idx]
            elif idx == len(categories):
                return "random"
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(categories) + 1}.")
        except ValueError:
            print(f"❌ Please enter a number between 1-{len(categories) + 1}.")


def get_category(provider_name: str, nsfw_allowed: bool) -> str:
    """
    Get image category selection based on provider.
    
    Args:
        provider_name: Name of the selected provider
        nsfw_allowed: Whether NSFW content is allowed
    
    Returns:
        str: Selected category
    """
    if provider_name == "waifu.im":
        return get_waifu_category(nsfw_allowed)
    elif provider_name == "nekos.moe":
        return get_catgirl_category(nsfw_allowed)
    
    categories = CATEGORIES.get(provider_name, [])
    
    if not categories:
        return input("\n📂 Enter image category (e.g., 'nature', 'animals'): ").strip()
    
    print("\n" + "=" * 50)
    print(f"📂 SELECT {provider_name.upper()} CATEGORY")
    print("=" * 50)
    
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat.capitalize()}")
    print(f"{len(categories) + 1}. Custom category")
    print("-" * 50)
    
    while True:
        choice = input(f"Enter your choice (1-{len(categories) + 1}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return categories[idx]
            elif idx == len(categories):
                custom = input("Enter custom category: ").strip()
                return custom if custom else "nature"
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(categories) + 1}.")
        except ValueError:
            print(f"❌ Please enter a number between 1-{len(categories) + 1}.")


def get_resolution() -> str:
    """
    Get wallpaper resolution selection.
    
    Returns:
        str: Selected resolution
    """
    print("\n" + "=" * 50)
    print("📐 SELECT RESOLUTION")
    print("=" * 50)
    
    for i, res in enumerate(RESOLUTIONS, 1):
        print(f"{i}. {res}")
    print(f"{len(RESOLUTIONS) + 1}. Custom resolution")
    print("-" * 50)
    
    while True:
        choice = input(f"Enter your choice (1-{len(RESOLUTIONS) + 1}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(RESOLUTIONS):
                return RESOLUTIONS[idx]
            elif idx == len(RESOLUTIONS):
                custom = input("Enter resolution (e.g., 1920x1080): ").strip()
                return custom if custom else RESOLUTIONS[0]
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(RESOLUTIONS) + 1}.")
        except ValueError:
            print(f"❌ Please enter a number between 1-{len(RESOLUTIONS) + 1}.")


def get_mood(provider_name: str) -> str:
    """
    Get mood/style filter for image search.
    
    Args:
        provider_name: Name of the selected provider
    
    Returns:
        str: Selected mood or empty string if no mood selection
    """
    moods = MOODS.get(provider_name, [""])
    
    # Filter out empty moods
    available_moods = [m for m in moods if m]
    
    if not available_moods:
        return ""
    
    print("\n" + "=" * 50)
    print(f"🎨 SELECT MOOD (Optional)")
    print("=" * 50)
    print("Leave blank to skip mood filter.")
    print("-" * 50)
    
    for i, mood in enumerate(available_moods, 1):
        print(f"{i}. {mood.capitalize()}")
    print(f"{len(available_moods) + 1}. Skip mood filter")
    print("-" * 50)
    
    while True:
        choice = input(f"Enter your choice (1-{len(available_moods) + 1}) or press Enter to skip: ").strip()
        
        if not choice or choice == str(len(available_moods) + 1):
            return ""
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available_moods):
                return available_moods[idx]
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(available_moods) + 1}.")
        except ValueError:
            print(f"❌ Please enter a number between 1-{len(available_moods) + 1}.")
