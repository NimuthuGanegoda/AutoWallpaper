# easy-wallpaper 🖼️

A simple, cross-platform Python CLI tool to download and set desktop wallpapers from multiple image sources.

## Features

- **Multi-source support** - Download from Pexels, Pixabay, or add your own
- **Interactive CLI** - Easy-to-use prompts for wallpaper preferences
- **Category-based search** - Choose from predefined categories (nature, space, cyberpunk, etc.) or enter custom ones
- **Resolution selection** - Pick from common resolutions (1920x1080, 2560x1440, 4K) or set custom
- **Mood filtering** - Optional mood filters (dark, light, vibrant, etc.)
- **Cross-platform support** - Works on Windows, macOS, and Linux (GNOME/feh/nitrogen)
- **Error handling** - Graceful error messages and helpful guidance

## Supported Image Providers

| Provider | API Key Required | Rate Limit | Notes |
|----------|------------------|------------|-------|
| **Pexels** | ❌ No | 200 req/hr | Photography, landscapes, real-world images |
| **Pixabay** | ✅ Yes | 100 req/hr | Diverse photography and illustrations |
| **waifu.im** | ❌ No | Unlimited | Anime, waifu, and manga-style artwork |

Adding new providers is easy - see [Contributing](#contributing).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NimuthuGanegoda/AutoWallpaper.git
   cd AutoWallpaper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Get API keys for additional providers:**

   **Pixabay (optional):**
   - Go to [Pixabay API](https://pixabay.com/api/)
   - Sign up and copy your API key
   - Set it: `export PIXABAY_API_KEY='your-api-key'`

   **Pexels (optional):**
   - Go to [Pexels API](https://www.pexels.com/api/)
   - Sign up and copy your API key
   - Set it: `export PEXELS_API_KEY='your-api-key'`

## Usage

Run the script:
```bash
python easy_wallpaper.py
```

The tool will guide you through:
1. **Selecting an image provider** (Pexels, Pixabay, etc.)
2. **Selecting a wallpaper category** (nature, space, architecture, etc.)
3. **Choosing a resolution** (1920x1080, 2560x1440, 4K, or custom)
4. **Optionally selecting a mood** (dark, light, vibrant, etc.)

The wallpaper will be downloaded and automatically set as your desktop background.

### Example Session

```
============================================================
🖼️  Welcome to easy-wallpaper!
============================================================

📷 Available image providers:
  1. Pexels          - High-quality images (no key required, 200 req/hour)
  2. Pixabay         - Diverse images (requires API key, 100 req/hour)
  3. waifu.im        - Anime waifu images (no key required, unlimited)

📸 Available categories:
  1. nature
  2. space
  3. cyberpunk
  ...

Select a category (1-11): 2

📐 Available resolutions:
  1. 1920x1080
  2. 2560x1440
  3. 3840x2160
  4. custom

Select resolution (1-4): 1

🎨 Moods (optional):
  1. dark
  2. light
  3. vibrant
  ...

Select mood (1-7) or skip: 1

⏳ Downloading from Pexels (space dark)...
✅ Download successful!
💾 Wallpaper saved to: /home/user/.wallpapers/wallpaper.jpg
✅ Wallpaper set successfully on Linux (GNOME)!

============================================================
🎉 All done! Enjoy your new wallpaper!
============================================================
```

## How It Works

### Code Structure

- **`ImageProvider` (ABC)** - Abstract base class for image sources
  - `PexelsProvider` - Implementation for Pexels
  - `PixabayProvider` - Implementation for Pixabay
  - `WaifuImProvider` - Implementation for waifu.im anime images
- **`get_provider()`** - Prompts user to select an image provider
- **`get_category()`** - Prompts user for wallpaper category
- **`get_resolution()`** - Prompts user for image resolution
- **`get_mood()`** - Optionally prompts user for mood filter
- **`save_wallpaper()`** - Saves image to `~/.wallpapers/`
- **`set_wallpaper()`** - Dispatches to OS-specific setter
- **`set_wallpaper_windows()`** - Uses Windows API via ctypes
- **`set_wallpaper_macos()`** - Uses AppleScript via osascript
- **`set_wallpaper_linux()`** - Uses gsettings (GNOME), feh, or nitrogen

### Wallpaper Storage

Downloaded wallpapers are saved to:
- **Linux/macOS:** `~/.wallpapers/wallpaper.jpg`
- **Windows:** `C:\Users\<username>\.wallpapers\wallpaper.jpg`

## Requirements

### Python
- Python 3.7+

### Dependencies
- `requests` - For HTTP requests to image providers

### OS-Specific Requirements

**Linux:**
- For GNOME: `gsettings` (usually pre-installed)
- Fallback options: `feh` or `nitrogen` if GNOME is not available

  Install feh:
  ```bash
  sudo apt install feh  # Debian/Ubuntu
  sudo pacman -S feh     # Arch
  ```

**macOS:**
- `osascript` (built-in)

**Windows:**
- No additional requirements (uses built-in Windows API)

## Environment Variables

- **`PEXELS_API_KEY`** (optional) - For higher Pexels rate limits
- **`PIXABAY_API_KEY`** (optional) - Required to use Pixabay provider

## Troubleshooting

### "No images found for..."
- Try a different category or mood
- Check your internet connection
- Verify the image provider is accessible from your region

### "API key not set" (for Pixabay)
- Pixabay requires a free API key
- Get one at [https://pixabay.com/api/](https://pixabay.com/api/)
- Set it: `export PIXABAY_API_KEY='your-key'`

### "Could not set wallpaper on Linux"
Install one of the supported tools:
```bash
sudo apt install feh nitrogen  # Debian/Ubuntu
```

### "Failed to download wallpaper"
- Check your internet connection
- Ensure you're not hitting the rate limit for your provider
- Try switching to a different provider

## Tips

- **Custom categories:** You can enter any search term as a custom category (e.g., "sunset mountains", "retro cars")
- **Automate wallpaper rotation:** Use cron (Linux/macOS) or Task Scheduler (Windows) to run the script periodically
- **Start with Pexels:** No API key needed and high rate limits for personal use

## Adding New Image Providers

It's easy to add support for new image sources! Follow these steps:

### 1. Create a new provider class

```python
class MyImageProvider(ImageProvider):
    """Image provider for MyImageService."""
    
    def __init__(self):
        self.api_url = "https://api.myimageservice.com/search"
        self.api_key = os.getenv("MY_SERVICE_API_KEY", "")
    
    def get_name(self) -> str:
        return "MyImageService"
    
    def get_description(self) -> str:
        return "My description (X req/hour)"
    
    def download_image(self, category: str, mood: str = "") -> bytes:
        # Implement your download logic here
        # Return the image bytes
        pass
```

### 2. Register the provider

Add to the `PROVIDERS` dict:
```python
PROVIDERS = {
    "1": PexelsProvider,
    "2": PixabayProvider,
    "3": MyImageProvider,  # Add your provider
}
```

### 3. Submit a pull request!

We'd love to add support for more providers.

## License

MIT

## Contributing

Contributions are welcome! Ideas:
- Add support for more image providers (Unsplash, Flickr, etc.)
- Improve wallpaper setting for other Linux desktop environments (KDE, Xfce)
- Add configuration file support
- Create a GUI version
- Add wallpaper scheduling/rotation

Feel free to open issues or submit pull requests!

## Resources

- [Pexels API Documentation](https://www.pexels.com/api/)
- [Pixabay API Documentation](https://pixabay.com/api/docs/)
- [Pexels](https://www.pexels.com/)
- [Pixabay](https://pixabay.com/)

