# 🖼️ Easy Wallpaper

A modular Python application that downloads beautiful wallpapers from multiple sources and automatically sets them on your desktop. Now with a Graphical User Interface (GUI)!

## ✨ Features

- **Multiple Image Providers**
  - 📸 **Pexels** - High-quality photos (200 requests/hour, no API key required)
  - 🎨 **Pixabay** - Diverse images and illustrations (100 requests/hour, API key required)
  - 👩 **waifu.im** - Anime waifu images (unlimited, no API key required)
  - 🐱 **nekos.moe** - Catgirl images (unlimited, no API key required)
  - 📷 **Unsplash** - Professional photos (50 requests/hour, Access Key required)
  - 🧱 **Wallhaven** - Anime & General wallpapers (API key optional)
  - 🌄 **Bing** - Daily wallpapers (Today, Yesterday, etc.)
  - 🎲 **Picsum** - Random placeholder images (Resolution based)
  - 🚀 **NASA APOD** - Astronomy Picture of the Day (Space images, API key optional)
  - 🐈 **TheCatAPI** - Random cat images
  - 🐕 **TheDogAPI** - Random dog images
  - 🏛️ **The Met** - Classic art from The Metropolitan Museum of Art
  - 🎨 **Art Institute of Chicago** - Classic and modern art
  - 👽 **Rick and Morty** - Character images from the show
  - 📚 **Open Library** - Book cover art
  - 🎲 **Random Source** - Surprise me! (Picks a random provider)

- **Cross-Platform Support**
  - ✅ Windows (using WinAPI)
  - ✅ macOS (using AppleScript/osascript)
  - ✅ Linux (using dconf, feh, pcmanfm-desktop, or nitrogen)

- **Customizable Options**
  - **GUI Mode** for easy interaction
  - Category selection for each provider
  - Mood/style filters (where available)
  - Resolution preference
  - API key support for premium providers

## 📋 Project Structure

```
AutoWallpaper/
├── main.py              # CLI Entry point
├── gui_main.py          # GUI Entry point
├── providers.py         # Image provider implementations
├── config.py            # Configuration and constants
├── ui.py                # CLI User interface and prompts
├── gui.py               # GUI implementation
├── wallpaper.py         # Wallpaper setting functionality
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

### Module Descriptions

**`main.py`** - CLI entry point that orchestrates the workflow.
**`gui_main.py`** - Entry point for the Graphical User Interface.
**`providers.py`** - Image provider implementations (Pexels, Unsplash, NASA, etc.).
**`config.py`** - Configuration and constants.
**`gui.py`** - Tkinter-based GUI implementation.
**`wallpaper.py`** - OS-specific wallpaper setting logic.

## 💻 Usage

### GUI Mode (Recommended)

Run the application with a graphical interface:
```bash
python gui_main.py
```

### CLI Usage

Run the application in interactive CLI mode:
```bash
python main.py
```

Or use command-line arguments for automation:
```bash
python main.py --provider 3 --category waifu --resolution 1920x1080 --loop 60
```
* Arguments:
  * `--provider`: Provider ID (see menu or config)
  * `--category`: Search category
  * `--mood`: Mood filter (optional)
  * `--resolution`: Target resolution (e.g., 1920x1080)
  * `--loop`: Loop interval in minutes (optional)

### Linux Requirements

On Linux, ensure you have one of the following installed to set the wallpaper:
- `feh` (for any X11 desktop)
- `dconf-cli` (for GNOME/Cinnamon)
- `pcmanfm-desktop` (for XFCE/LXDE)
- `nitrogen` (generic X11)

```bash
sudo apt install feh  # Example
```

## ⚙️ Configuration

### Environment Variables (API Keys)

Some providers require API keys. Set them as environment variables:

```bash
# Linux/macOS
export PEXELS_API_KEY='your-key'
export PIXABAY_API_KEY='your-key'
export UNSPLASH_ACCESS_KEY='your-key'
export WALLHAVEN_API_KEY='your-key' # Optional
export NASA_API_KEY='your-key'      # Optional (defaults to DEMO_KEY)

# Windows (PowerShell)
$env:PEXELS_API_KEY='your-key'
```

## 📁 Wallpaper Storage

Downloaded wallpapers are saved to:
- **Windows**: `%APPDATA%\Roaming\easy-wallpaper\`
- **macOS/Linux**: `~/.easy-wallpaper/`

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Credits

- [Pexels](https://www.pexels.com/)
- [Pixabay](https://pixabay.com/)
- [waifu.im](https://waifu.im/)
- [nekos.moe](https://nekos.moe/)
- [Unsplash](https://unsplash.com/)
- [Wallhaven](https://wallhaven.cc/)
- [Bing](https://www.bing.com/)
- [Lorem Picsum](https://picsum.photos/)
- [NASA APOD](https://api.nasa.gov/)
- [TheCatAPI](https://thecatapi.com/)
- [TheDogAPI](https://thedogapi.com/)
- [The Met Museum](https://www.metmuseum.org/)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
