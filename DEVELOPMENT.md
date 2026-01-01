# easy-wallpaper Development Guide

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone https://github.com/NimuthuGanegoda/AutoWallpaper.git
   cd AutoWallpaper
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements-dev.txt
   ```

2. **Get Unsplash API key:**
   - Visit [Unsplash Developers](https://unsplash.com/developers)
   - Create an app and copy the Access Key
   - Set it: `export UNSPLASH_API_KEY='your-key'`

3. **Run the tool:**
   ```bash
   python easy_wallpaper.py
   ```

## Code Organization

```
easy_wallpaper.py
├── Configuration
│   ├── API endpoint and default settings
│   └── Lists of categories and moods
├── User Input Functions
│   ├── get_category()
│   ├── get_resolution()
│   └── get_mood()
├── Download Functions
│   ├── download_wallpaper()
│   └── save_wallpaper()
├── OS-Specific Setters
│   ├── set_wallpaper_windows()
│   ├── set_wallpaper_macos()
│   ├── set_wallpaper_linux()
│   └── set_wallpaper() - dispatcher
└── main()
```

## Code Quality

Format and check code:
```bash
# Format code
black easy_wallpaper.py

# Sort imports
isort easy_wallpaper.py

# Lint
flake8 easy_wallpaper.py

# Type check
mypy easy_wallpaper.py
```

## Future Enhancements

- [ ] Config file support (JSON/YAML) for saved preferences
- [ ] Wallpaper history and favorites
- [ ] Scheduled/automatic wallpaper rotation
- [ ] GUI version using tkinter or PyQt
- [ ] Support for other image sources (Bing, Pexels, Pixabay)
- [ ] Unit tests for download and wallpaper logic
- [ ] Package distribution on PyPI

## Notes

- The tool stores downloaded wallpapers in `~/.wallpapers/`
- Unsplash API free tier: 50 requests/hour
- Each API call fetches a new random image
