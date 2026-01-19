# 🖼️ Easy Wallpaper

A modular Python application that downloads beautiful wallpapers from multiple sources and automatically sets them on your desktop.

## ✨ Features

- **Multiple Image Providers**
  - 📸 **Pexels** - High-quality photos (200 requests/hour, no API key required)
  - 🎨 **Pixabay** - Diverse images and illustrations (100 requests/hour, API key required)
  - 👩 **waifu.im** - Anime waifu images (unlimited, no API key required)
  - 🐱 **nekos.moe** - Catgirl images (unlimited, no API key required)
  - 🌊 **Unsplash** - Professional photos (requires API key)
  - 🎲 **Picsum** - Random placeholder images (no key required)
  - 🖼️ **Wallhaven** - Anime & General wallpapers (key optional)
  - 📅 **Bing** - Daily wallpaper (no key required)

- **Cross-Platform Support**
  - ✅ Windows (using WinAPI)
  - ✅ macOS (using AppleScript/osascript)
  - ✅ Linux (using dconf, feh, pcmanfm-desktop, or nitrogen)

- **Customizable Options**
  - Category selection for each provider
  - Mood/style filters (where available)
  - Resolution preference
  - API key support for premium providers
  - **Scheduled Updates**: Run in a loop to change wallpaper automatically

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
- Handles CLI arguments and scheduling loops

**`providers.py`** - Image provider implementations:
- `ImageProvider` (ABC) - Base class for all providers
- `PexelsProvider` - Pexels photo provider
- `PixabayProvider` - Pixabay illustration provider
- `WaifuImProvider` - waifu.im anime provider
- `CatgirlProvider` - nekos.moe catgirl provider
- `UnsplashProvider` - Unsplash photo provider
- `PicsumProvider` - Picsum random images
- `WallhavenProvider` - Wallhaven wallpapers
- `BingProvider` - Bing daily wallpaper

**`config.py`** - Configuration and constants

## 💻 Usage

### Basic Usage (Interactive Mode)

Run the application without arguments to use the interactive menu:
```bash
python main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### CLI / Scheduled Usage

You can automate wallpaper updates using command-line arguments:

```bash
# Update once from waifu.im
python main.py --provider "waifu.im" --category "maid"

# Update once from Wallhaven
python main.py --provider "Wallhaven" --category "cyberpunk"

# Run in a loop (update every 60 minutes)
python main.py --provider "Picsum" --loop 60
```

**Arguments:**
- `-p`, `--provider`: Provider ID (1-8) or Name (e.g., "Unsplash")
- `-c`, `--category`: Image category (e.g., "nature", "random")
- `-m`, `--mood`: Image mood (optional)
- `-r`, `--resolution`: Resolution (default: 1920x1080)
- `-l`, `--loop`: Loop interval in minutes (keeps running)

### Interactive Menu

The application will guide you through:
1. **Select Image Provider** - Choose from available providers
2. **Select Category** - Choose from available categories for that provider
3. **Select Mood** (optional) - Filter by mood/style if available
4. **Select Resolution** - Choose your desired wallpaper resolution
5. **Download & Set** - The app downloads and sets the wallpaper automatically

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
    # ...
    "9": MyProvider(),  # Add here
}

CATEGORIES = {
    "My Provider": ["category1", "category2", ...],
    # ... other providers
}
```

3. Update the menu in `ui.py` if needed (it updates automatically based on config)

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
export PEXELS_API_KEY='your-key'
export UNSPLASH_ACCESS_KEY='your-key'
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

- [Pexels](https://www.pexels.com/)
- [Pixabay](https://pixabay.com/)
- [waifu.im](https://waifu.im/)
- [nekos.moe](https://nekos.moe/)
- [Unsplash](https://unsplash.com/)
- [Picsum](https://picsum.photos/)
- [Wallhaven](https://wallhaven.cc/)
- [Bing](https://www.bing.com/)

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
