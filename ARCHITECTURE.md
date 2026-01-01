# AutoWallpaper - Module Architecture

## Project Structure

```
AutoWallpaper/
│
├── main.py                 # 🎯 Entry point - Orchestrates workflow
│   └── Imports: ui, wallpaper, config
│
├── providers.py            # 📡 Image provider implementations
│   ├── ImageProvider (ABC)
│   ├── PexelsProvider
│   ├── PixabayProvider
│   ├── WaifuImProvider
│   └── CatgirlProvider
│
├── config.py               # ⚙️ Configuration & constants
│   ├── PROVIDERS
│   ├── CATEGORIES
│   ├── MOODS
│   └── RESOLUTIONS
│
├── ui.py                   # 💬 User interaction
│   ├── get_provider()
│   ├── get_category()
│   ├── get_mood()
│   ├── get_resolution()
│   └── Provider-specific menus
│
├── wallpaper.py            # 🖼️ Wallpaper management
│   ├── save_wallpaper()
│   ├── set_wallpaper()
│   ├── set_wallpaper_windows()
│   ├── set_wallpaper_macos()
│   └── set_wallpaper_linux()
│
├── requirements.txt        # 📦 Dependencies
├── README.md               # 📖 Documentation
├── REFACTORING.md          # 📝 Refactoring notes
└── ARCHITECTURE.md         # 📐 This file
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                      │
│                      (Interactive Menus)                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │     main.py          │
        │  (Orchestration)     │
        └──────────┬───────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌──────────┐
    │  ui.py │ │config. │ │wallpaper │
    │        │ │  py    │ │   .py    │
    └────┬───┘ └──┬─────┘ └─────┬────┘
         │        │             │
         ▼        ▼             ▼
    ┌──────────────────┐    ┌─────────────┐
    │  providers.py    │    │ save_image  │
    │                  │    │ set_wallpap │
    │ • PexelsProvider │    └─────────────┘
    │ • PixabayProvider│
    │ • WaifuImProvid  │
    │ • CatgirlProvider│
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │   DOWNLOAD IMAGE │
    │   FROM PROVIDER  │
    │   (HTTP Request) │
    └──────────────────┘
```

## Module Dependencies

```
main.py
├── ui.py
│   └── config.py
├── config.py
│   └── providers.py
├── providers.py
│   └── (requests library)
└── wallpaper.py
    └── (os, platform, subprocess, ctypes)
```

## Execution Flow

### 1. User starts the app
```bash
python main.py
```

### 2. Main orchestrates the workflow
```
main()
├─ ui.get_provider()           → Select provider (PROVIDERS from config)
├─ ui.get_category()           → Select category (CATEGORIES from config)
├─ ui.get_mood()               → Select mood (MOODS from config)
├─ ui.get_resolution()         → Select resolution (RESOLUTIONS from config)
├─ provider.download_image()   → Get image bytes
├─ wallpaper.save_wallpaper()  → Save to ~/.easy-wallpaper/
└─ wallpaper.set_wallpaper()   → Set based on OS
    ├─ Windows: set_wallpaper_windows()
    ├─ macOS: set_wallpaper_macos()
    └─ Linux: set_wallpaper_linux()
```

## Class Hierarchy

```
ImageProvider (ABC)
├── PexelsProvider
├── PixabayProvider
├── WaifuImProvider
└── CatgirlProvider
```

All concrete providers implement:
- `get_name()` → str
- `get_description()` → str
- `download_image(category: str, mood: str) → bytes`

## Function Call Hierarchy

```
main()
│
├─ get_provider() [ui]
│  └─ Returns: (provider_key, provider_instance)
│
├─ get_category(provider_name) [ui]
│  ├─ get_waifu_category() [ui]
│  ├─ get_catgirl_category() [ui]
│  └─ Returns: category_string
│
├─ get_mood(provider_name) [ui]
│  └─ Returns: mood_string
│
├─ get_resolution() [ui]
│  └─ Returns: resolution_string
│
├─ provider.download_image(category, mood) [providers]
│  └─ Returns: image_bytes
│
├─ save_wallpaper(image_data) [wallpaper]
│  └─ Returns: file_path
│
└─ set_wallpaper(file_path) [wallpaper]
   ├─ set_wallpaper_windows(path)
   ├─ set_wallpaper_macos(path)
   └─ set_wallpaper_linux(path)
```

## Configuration Structure

### PROVIDERS (config.py)
```python
PROVIDERS = {
    "1": PexelsProvider(),
    "2": PixabayProvider(),
    "3": WaifuImProvider(),
    "4": CatgirlProvider(),
}
```

### CATEGORIES (config.py)
```python
CATEGORIES = {
    "Pexels": ["nature", "landscape", "urban", ...],
    "Pixabay": ["abstract", "animals", "art", ...],
    "waifu.im": ["waifu", "maid", "miko", ...],
    "nekos.moe": ["safe sfw", "nsfw", "mixed"],
}
```

### MOODS (config.py)
```python
MOODS = {
    "Pexels": ["calm", "vibrant", "dark", "bright"],
    "Pixabay": ["colorful", "minimal", "artistic", "realistic"],
    "waifu.im": [""],  # No mood filtering
    "nekos.moe": [""],  # No mood filtering
}
```

## Extension Points

### Adding a New Provider

1. **Create class in providers.py**
```python
class MyProvider(ImageProvider):
    def get_name(self) -> str:
        return "My Provider"
    
    def get_description(self) -> str:
        return "Description"
    
    def download_image(self, category: str, mood: str = "") -> bytes:
        # Implementation
        pass
```

2. **Register in config.py**
```python
PROVIDERS = {
    # ... existing
    "5": MyProvider(),
}

CATEGORIES = {
    # ... existing
    "My Provider": ["cat1", "cat2", ...],
}
```

3. **Update menu in ui.py** (if needed)

### Adding a New Resolution

Edit `config.py`:
```python
RESOLUTIONS = [
    "1920x1080",
    "2560x1440",
    "3840x2160",
    "7680x4320",  # Add new resolution
]
```

### Adding New Categories

Edit `config.py` CATEGORIES:
```python
CATEGORIES = {
    "Pexels": [
        "nature",
        "landscape",
        # Add new category
        "mountains",
    ],
    # ...
}
```

## Error Handling Strategy

```
main()
  │
  ├─ User cancellation (Ctrl+C)
  │  └─ Catch KeyboardInterrupt → "Operation cancelled"
  │
  ├─ Provider errors
  │  └─ Catch RuntimeError → Display error message
  │     (API failures, no images found, rate limit)
  │
  ├─ Wallpaper setting errors
  │  └─ Catch RuntimeError → Display platform-specific help
  │     (missing tools, permissions)
  │
  └─ Unexpected errors
     └─ Catch Exception → Generic error message
```

## Module Responsibilities

| Module | Responsibility | Imports |
|--------|-----------------|---------|
| **main.py** | Orchestrate workflow | ui, config, wallpaper |
| **providers.py** | Download images | requests |
| **config.py** | Store constants | providers |
| **ui.py** | User interaction | config |
| **wallpaper.py** | Save & set wallpaper | os, platform, subprocess, ctypes |

## Testing Strategy

### Unit Tests
- `test_providers.py` - Mock API responses
- `test_wallpaper.py` - Mock OS calls
- `test_ui.py` - Mock user input
- `test_config.py` - Verify constants

### Integration Tests
- Test provider → download → save → set flow
- Test on different operating systems

### Manual Tests
- Test each provider individually
- Test each OS wallpaper setter
- Test error scenarios

## Performance Considerations

- **Image Downloads**: Parallel downloads (if multiple images needed)
- **Provider Caching**: Consider caching provider responses
- **Memory**: Stream large images instead of loading fully
- **Startup Time**: Lazy load providers as needed

## Future Architecture

```
┌─────────────────────────────────────┐
│     GUI Layer (tkinter/PyQt)        │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│   CLI Layer (current main.py)       │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│   Core API (providers + wallpaper)  │
└─────────────────────────────────────┘
```

---

**This architecture follows SOLID principles and is easily maintainable and extensible!** 🏗️
