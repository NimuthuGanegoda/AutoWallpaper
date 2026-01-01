# Module Dependency Map

## Import Graph

```
main.py
├── from ui import (get_provider, get_category, get_mood, get_resolution)
│   └── ui.py
│       └── from config import (PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS)
│           └── config.py
│               └── from providers import (PexelsProvider, PixabayProvider, 
│                                          WaifuImProvider, CatgirlProvider)
│                   └── providers.py
│                       └── import requests
│
├── from wallpaper import (save_wallpaper, set_wallpaper)
│   └── wallpaper.py
│       ├── import os
│       ├── import platform
│       ├── import subprocess
│       └── import ctypes (Windows only)
│
└── (No direct import of config, accessed through ui)
```

## Circular Dependency Analysis

✅ **No circular dependencies detected!**

The dependency graph is acyclic (DAG):
```
providers.py (no imports)
    ↑
config.py
    ↑
ui.py
    ↑
main.py
    ↑
wallpaper.py (independent)
```

## Module Interaction Matrix

|       | main | ui | config | providers | wallpaper |
|-------|------|-----|--------|-----------|-----------|
| **main** | - | ✓ import | - | - | ✓ import |
| **ui** | - | - | ✓ import | - | - |
| **config** | - | - | - | ✓ import | - |
| **providers** | - | - | - | - | - |
| **wallpaper** | - | - | - | - | - |

## Public API by Module

### `main.py`
```python
def main() -> None
```
- **Usage**: `python main.py` (command line entry point)
- **Purpose**: Orchestrate the entire application flow

### `providers.py`
```python
class ImageProvider(ABC):
    @abstractmethod
    def get_name(self) -> str
    @abstractmethod
    def get_description(self) -> str
    @abstractmethod
    def download_image(self, category: str, mood: str = "") -> bytes

class PexelsProvider(ImageProvider): ...
class PixabayProvider(ImageProvider): ...
class WaifuImProvider(ImageProvider): ...
class CatgirlProvider(ImageProvider): ...
```

### `config.py`
```python
PROVIDERS: Dict[str, ImageProvider]
CATEGORIES: Dict[str, List[str]]
MOODS: Dict[str, List[str]]
RESOLUTIONS: List[str]

DEFAULT_PROVIDER: str = "3"
DEFAULT_CATEGORY: str = "waifu"
DEFAULT_RESOLUTION: str = "1920x1080"
```

### `ui.py`
```python
def get_provider() -> Tuple[str, ImageProvider]
def get_os_choice() -> str
def get_waifu_category() -> str
def get_catgirl_category() -> str
def get_category(provider_name: str) -> str
def get_resolution() -> str
def get_mood(provider_name: str) -> str
```

### `wallpaper.py`
```python
def save_wallpaper(image_data: bytes, filename: str = "wallpaper.png") -> str
def set_wallpaper(image_path: str) -> None
def set_wallpaper_windows(image_path: str) -> None
def set_wallpaper_macos(image_path: str) -> None
def set_wallpaper_linux(image_path: str) -> None
```

## Data Flow Between Modules

### Scenario 1: Basic Workflow
```
User Input
    ↓
ui.get_provider()
    ↓ (returns provider instance from config.PROVIDERS)
ui.get_category()
    ↓ (uses config.CATEGORIES)
ui.get_mood()
    ↓ (uses config.MOODS)
ui.get_resolution()
    ↓ (uses config.RESOLUTIONS)
provider.download_image()
    ↓ (returns image bytes)
wallpaper.save_wallpaper()
    ↓ (returns file path)
wallpaper.set_wallpaper()
    ↓
✅ Wallpaper Set
```

### Scenario 2: Provider Selection
```
ui.get_provider()
    ↓
Looks up config.PROVIDERS["1|2|3|4"]
    ↓
Returns (key, ImageProvider instance)
    ↓
main() stores in variable: provider
    ↓
provider.download_image() called later
```

### Scenario 3: Category Selection
```
ui.get_category(provider_name="waifu.im")
    ↓
Looks up config.CATEGORIES["waifu.im"]
    ↓
Displays menu and gets user choice
    ↓
Returns selected category string
    ↓
provider.download_image(category=result)
```

## Import Dependencies List

### main.py imports:
- `from ui import get_provider, get_category, get_mood, get_resolution`
- `from wallpaper import save_wallpaper, set_wallpaper`
- `import sys`
- `from pathlib import Path`

### ui.py imports:
- `from config import PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS`

### config.py imports:
- `from providers import PexelsProvider, PixabayProvider, WaifuImProvider, CatgirlProvider`

### providers.py imports:
- `import os`
- `from abc import ABC, abstractmethod`
- `import requests`

### wallpaper.py imports:
- `import os`
- `import platform`
- `import subprocess`
- `from pathlib import Path`
- `import ctypes` (Windows only, wrapped in function)
- `from ctypes import wintypes` (Windows only, wrapped in function)

## External Dependencies

### Required
- `requests` - HTTP requests for API calls
  - Used in: `providers.py` (all provider classes)

### Built-in (No installation needed)
- `os` - File system and environment variables
- `sys` - Command line arguments
- `platform` - OS detection
- `subprocess` - Execute system commands
- `ctypes` - Windows API access
- `pathlib` - Path handling
- `abc` - Abstract base classes
- `re` - Regular expressions (if added)

## Dependency Tree by Module

```
main.py
├── Level 1
│   ├── ui.py
│   │   └── Level 2
│   │       └── config.py
│   │           └── Level 3
│   │               └── providers.py
│   │                   └── Level 4
│   │                       └── requests (external)
│   └── wallpaper.py
│       └── os, platform, subprocess (built-in)
└── sys, pathlib (built-in)
```

## Module Coupling Analysis

### Tight Coupling (Acceptable)
- `config.py` depends on `providers.py` - Creates instances
- `ui.py` depends on `config.py` - Reads configuration
- `main.py` depends on `ui.py` and `wallpaper.py` - Orchestrates workflow

**Rationale**: These are intentional design dependencies representing proper separation of concerns.

### Loose Coupling (Good)
- `main.py` only depends on public APIs
- `providers.py` is independent (no internal module imports)
- `wallpaper.py` is independent (only uses built-in modules)

## Extension Points (Low Coupling)

### Adding a Provider (No changes needed in other modules)
1. Create new class in `providers.py`
2. Add instance to `config.PROVIDERS`
3. Add categories to `config.CATEGORIES`
4. **Done!** - No changes to `main.py`, `ui.py`, or `wallpaper.py`

### Adding UI Feature
1. Add function to `ui.py`
2. Call from `main.py`
3. **Done!** - No changes to other modules

### Changing Wallpaper Backend
1. Modify only `wallpaper.py`
2. Keep same function signatures
3. **Done!** - `main.py` doesn't need changes

## Code Metrics

| Module | Lines | Functions/Classes | Imports | Public API |
|--------|-------|-------------------|---------|------------|
| main.py | 147 | 1 function | 3 | 1 entry point |
| providers.py | 408 | 4 classes + ABC | 3 | 1 ABC + 4 classes |
| config.py | 55 | 0 (data only) | 1 | 5 constants |
| ui.py | 333 | 7 functions | 1 | 7 functions |
| wallpaper.py | 308 | 5 functions | 4-5 | 5 functions |
| **Total** | **1251** | **17** | - | - |

## Change Impact Analysis

### If you modify `providers.py`
- **Impact**: `config.py` (uses provider classes)
- **Cascade**: `ui.py`, `main.py`
- **Severity**: Medium (provider interface changes)

### If you modify `config.py`
- **Impact**: `ui.py` (reads configuration)
- **Cascade**: `main.py`
- **Severity**: Low (just constants)

### If you modify `ui.py`
- **Impact**: `main.py` (calls UI functions)
- **Cascade**: None
- **Severity**: Low (UI-only change)

### If you modify `wallpaper.py`
- **Impact**: `main.py` (calls wallpaper functions)
- **Cascade**: None
- **Severity**: Low (independent module)

### If you modify `main.py`
- **Impact**: None (orchestrator only)
- **Cascade**: None
- **Severity**: None

## Testability Ranking

1. **providers.py** ⭐⭐⭐⭐⭐
   - Easy to mock requests
   - No dependencies on other modules
   - Clear interface (ImageProvider ABC)

2. **wallpaper.py** ⭐⭐⭐⭐⭐
   - Easy to mock OS calls
   - No dependencies on other modules
   - Platform detection clear

3. **config.py** ⭐⭐⭐⭐⭐
   - No logic to test
   - Just data
   - Can be replaced with JSON

4. **ui.py** ⭐⭐⭐⭐
   - Can mock config
   - Input/output clear
   - User interaction requires testing

5. **main.py** ⭐⭐⭐
   - All dependencies are mockable
   - Integration testing needed
   - Flow logic complex

---

**Perfect dependency structure for a maintainable application!** ✨
