# 🚀 Quick Reference Guide

## File Locations & Purposes

| File | Lines | Purpose |
|------|-------|---------|
| **main.py** | 89 | Entry point - orchestrates the application flow |
| **providers.py** | 299 | Image provider implementations (Pexels, Pixabay, waifu.im, nekos.moe) |
| **config.py** | 81 | Configuration constants (PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS) |
| **ui.py** | 247 | User interaction prompts and menus |
| **wallpaper.py** | 249 | Wallpaper saving and setting (Windows/macOS/Linux) |

## How to Use

### Run the Application
```bash
python main.py
```

### Add a New Image Provider

1. **Create provider class in `providers.py`**:
```python
class MyProvider(ImageProvider):
    def get_name(self) -> str:
        return "My Provider"
    
    def get_description(self) -> str:
        return "My provider description"
    
    def download_image(self, category: str, mood: str = "") -> bytes:
        # Download logic here
        pass
```

2. **Register in `config.py`**:
```python
PROVIDERS = {
    "1": PexelsProvider(),
    "2": PixabayProvider(),
    "3": WaifuImProvider(),
    "4": CatgirlProvider(),
    "5": MyProvider(),  # Add here
}

CATEGORIES = {
    "My Provider": ["cat1", "cat2", ...],
    # ... other providers
}
```

3. Done! No other changes needed.

### Add New Categories

Edit `config.py`:
```python
CATEGORIES = {
    "Pexels": ["nature", "landscape", "mountains", ...],  # Add here
    # ... other providers
}
```

### Add New Resolutions

Edit `config.py`:
```python
RESOLUTIONS = [
    "1920x1080",
    "2560x1440",
    "3840x2160",
    "7680x4320",  # Add new resolution
]
```

## Module Import Cheat Sheet

### In main.py
```python
from ui import get_provider, get_category, get_mood, get_resolution
from wallpaper import save_wallpaper, set_wallpaper
```

### In ui.py
```python
from config import PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS
```

### In config.py
```python
from providers import PexelsProvider, PixabayProvider, WaifuImProvider, CatgirlProvider
```

### In providers.py
```python
import requests
from abc import ABC, abstractmethod
```

### In wallpaper.py
```python
import os, platform, subprocess
from pathlib import Path
```

## Common Functions

### providers.py
```python
# Download image from provider
image_bytes = provider.download_image(category="nature", mood="calm")
```

### wallpaper.py
```python
# Save image to disk
path = save_wallpaper(image_bytes, filename="wallpaper.png")

# Set wallpaper (detects OS automatically)
set_wallpaper(path)
```

### ui.py
```python
# Get provider from user
key, provider = get_provider()

# Get category
category = get_category(provider.get_name())

# Get mood filter
mood = get_mood(provider.get_name())

# Get resolution
resolution = get_resolution()
```

## Error Handling

### Provider Errors
```python
try:
    image_data = provider.download_image("nature")
except RuntimeError as e:
    print(f"Download failed: {e}")
```

### Wallpaper Setting Errors
```python
try:
    set_wallpaper(path)
except RuntimeError as e:
    print(f"Setting wallpaper failed: {e}")
```

## Data Structures

### PROVIDERS Dict
```python
PROVIDERS = {
    "1": PexelsProvider(),      # Key → Instance mapping
    "2": PixabayProvider(),
    "3": WaifuImProvider(),
    "4": CatgirlProvider(),
}
```

### CATEGORIES Dict
```python
CATEGORIES = {
    "Pexels": ["nature", "landscape", "urban"],
    "Pixabay": ["abstract", "animals", "art"],
    "waifu.im": ["waifu", "maid", "miko"],
    "nekos.moe": ["safe sfw", "nsfw"],
}
```

### MOODS Dict
```python
MOODS = {
    "Pexels": ["calm", "vibrant", "dark"],
    "Pixabay": ["colorful", "minimal"],
    "waifu.im": [""],  # No moods
    "nekos.moe": [""],  # No moods
}
```

## Workflow Diagram

```
User → UI → Config → Provider → Download → Save → Set Wallpaper
      (menu) (data) (download)  (bytes)  (disk) (OS-specific)
```

## Environment Variables

```bash
# Optional: Pexels API key
export PEXELS_API_KEY='your-key-here'

# Required: Pixabay API key
export PIXABAY_API_KEY='your-key-here'
```

## Wallpaper Directories

- **Windows**: `%APPDATA%\Roaming\easy-wallpaper\`
- **macOS**: `~/.easy-wallpaper/`
- **Linux**: `~/.easy-wallpaper/`

## Class Inheritance

```
ImageProvider (ABC)
├── PexelsProvider
├── PixabayProvider  
├── WaifuImProvider
└── CatgirlProvider
```

All providers implement:
- `get_name()` → str
- `get_description()` → str
- `download_image(category, mood)` → bytes

## Testing Tips

### Test a Provider Directly
```python
from providers import PexelsProvider
provider = PexelsProvider()
image = provider.download_image("nature")
print(f"Downloaded {len(image)} bytes")
```

### Test Wallpaper Saving
```python
from wallpaper import save_wallpaper
import os

# Create dummy image
dummy_image = b'\x89PNG\r\n\x1a\n'  # PNG header

path = save_wallpaper(dummy_image)
print(f"Saved to: {path}")
print(f"File exists: {os.path.exists(path)}")
```

### Test Configuration
```python
from config import PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS

print(f"Providers: {list(PROVIDERS.keys())}")
print(f"Categories: {CATEGORIES}")
print(f"Resolutions: {RESOLUTIONS}")
```

## Troubleshooting

### "ModuleNotFoundError"
- Ensure all .py files are in the same directory
- Run from the AutoWallpaper directory

### "No images found"
- Try a different category
- Check internet connection
- Verify API key if using Pixabay

### "Wallpaper not setting on Linux"
- Install: `sudo apt install feh`
- Or: `sudo apt install dconf-cli`

## Performance Optimization

- Wallpapers saved to `~/.easy-wallpaper/` - reusable across runs
- Provider instances created once in `config.py`
- API calls happen only when user requests download

## Dependency Visualization

```
main.py
├── ui.py
│   └── config.py
│       └── providers.py
│           └── requests
└── wallpaper.py
    └── os, platform, subprocess
```

## Next Steps

1. **Add More Providers** - Follow the provider template
2. **Create GUI** - Import ui functions into tkinter/PyQt
3. **Add Tests** - Use pytest to test modules
4. **Configuration File** - Load settings from JSON
5. **Daemon Mode** - Schedule wallpaper changes

---

**Happy wallpaper downloading! 🎉**
