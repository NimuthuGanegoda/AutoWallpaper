# 🖼️ Easy Wallpaper

A modular Python application that downloads beautiful wallpapers from multiple sources and automatically sets them on your desktop.

## ✨ Features

- **Multiple Image Providers**
  - 📸 **Pexels** - High-quality photos (200 requests/hour, no API key required)
  - 🎨 **Pixabay** - Diverse images and illustrations (100 requests/hour, API key required)
  - 👩 **waifu.im** - Anime waifu images (unlimited, no API key required)
  - 🐱 **nekos.moe** - Catgirl images (unlimited, no API key required)

- **Cross-Platform Support**
  - ✅ Windows (using WinAPI)
  - ✅ macOS (using AppleScript/osascript)
  - ✅ Linux (using dconf, feh, pcmanfm-desktop, or nitrogen)

- **Customizable Options**
  - Category selection for each provider
  - Mood/style filters (where available)
  - Resolution preference
  - API key support for premium providers

## 📋 Project Structure

```
AutoWallpaper/
├── main.py              # Entry point
├── providers.py         # Image provider implementations
├── config.py            # Configuration and constants
├── ui.py                # User interface and prompts
├── wallpaper.py         # Wallpaper setting functionality
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

### Module Descriptions

**`main.py`** - Main entry point that orchestrates the workflow:
- Gets user inputs for provider, category, mood, and resolution
- Coordinates image download, saving, and wallpaper setting

**`providers.py`** - Image provider implementations:
- `ImageProvider` (ABC) - Base class for all providers
- `PexelsProvider` - Pexels photo provider
- `PixabayProvider` - Pixabay illustration provider
- `WaifuImProvider` - waifu.im anime provider
- `CatgirlProvider` - nekos.moe catgirl provider

**`config.py`** - Configuration and constants:

## 💻 Usage

### Basic Usage

Run the application:
```bash
python main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### Interactive Menu

The application will guide you through:
1. **Select Image Provider** - Choose between Pexels, Pixabay, waifu.im, or nekos.moe
2. **Select Category** - Choose from available categories for that provider
3. **Select Mood** (optional) - Filter by mood/style if available
4. **Select Resolution** - Choose your desired wallpaper resolution
5. **Download & Set** - The app downloads and sets the wallpaper automatically

### Example Session

```
🖼️  WELCOME TO EASY WALLPAPER

==================================================
📱 SELECT IMAGE PROVIDER
==================================================
1. Pexels      - High-quality photos (200 req/hour)
2. Pixabay     - Diverse images (100 req/hour, API key required)
3. waifu.im    - Anime waifu (unlimited)
4. nekos.moe   - Catgirls (unlimited)
--------------------------------------------------
Enter your choice (1-4): 3
✅ Selected: waifu.im

==================================================
👩 SELECT WAIFU CATEGORY
==================================================
1. Waifu
2. Maid
3. Miko
4. Oppai
5. Uniform
6. Kitsune
7. Demon
8. Elf
9. Random
--------------------------------------------------
Enter your choice (1-9): 1
✅ Selected category: waifu

==================================================
📐 SELECT RESOLUTION
==================================================
1. 1920x1080
2. 1366x768
3. 1280x720
4. 2560x1440
5. 3840x2160
6. Custom resolution
--------------------------------------------------
Enter your choice (1-6): 1
✅ Selected resolution: 1920x1080

==================================================
⏳ DOWNLOADING WALLPAPER
==================================================
⏳ Downloading from waifu.im (waifu)...
✅ Download successful!
💾 Wallpaper saved to: /home/user/.easy-wallpaper/wallpaper.png

==================================================
🎨 SETTING WALLPAPER
==================================================
✅ Wallpaper set successfully!

==================================================
✨ SUCCESS!
==================================================
Your new wallpaper has been set successfully!
Provider: waifu.im
Category: waifu
Saved to: /home/user/.easy-wallpaper/wallpaper.png
==================================================
```

## 🛠️ Extending the Application

### Adding a New Provider

1. Create a new class inheriting from `ImageProvider` in `providers.py`:

```python
class MyProvider(ImageProvider):
    def get_name(self) -> str:
        return "My Provider"
    
    def get_description(self) -> str:
        return "My Provider Description"
    
    def download_image(self, category: str, mood: str = "") -> bytes:
        # Implementation here
        pass
```

2. Register it in `config.py`:

```python
PROVIDERS = {
    "1": PexelsProvider(),
    "2": PixabayProvider(),
    "3": WaifuImProvider(),
    "4": CatgirlProvider(),
    "5": MyProvider(),  # Add here
}

CATEGORIES = {
    "My Provider": ["category1", "category2", ...],
    # ... other providers
}
```

3. Update the menu in `ui.py` if needed

## 📁 Wallpaper Storage

Downloaded wallpapers are saved to:
- **Windows**: `%APPDATA%\Roaming\easy-wallpaper\`
- **macOS**: `~/.easy-wallpaper/`
- **Linux**: `~/.easy-wallpaper/`

## ⚙️ Configuration

Edit `config.py` to customize:
- Available categories for each provider
- Default provider and category
- Available resolutions
- Default values

## 🐛 Troubleshooting

### "Module not found" errors
Make sure all modules are in the same directory and run with:
```bash
python main.py
```

### API key errors
Ensure API keys are set as environment variables:
```bash
echo $PEXELS_API_KEY  # Check if set
export PEXELS_API_KEY='your-key'  # Set if missing
```

### Linux wallpaper not setting
Install one of the required wallpaper tools:
```bash
sudo apt install feh  # For any X11 desktop
sudo apt install dconf-cli  # For GNOME
sudo apt install pcmanfm-desktop  # For XFCE/LXDE
```

### macOS wallpaper not setting
Ensure you allow the script to control your computer:
- System Preferences → Security & Privacy → Accessibility
- Add Terminal (or your Python IDE) to the allowed apps

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Credits

- [Pexels](https://www.pexels.com/) - Free stock photos
- [Pixabay](https://pixabay.com/) - Free images and vectors
- [waifu.im](https://waifu.im/) - Anime image API
- [nekos.moe](https://nekos.moe/) - Anime catgirl images

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Enjoy beautiful wallpapers! 🖼️✨**

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

