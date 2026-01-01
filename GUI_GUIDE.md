# 🖼️ AutoWallpaper GUI Guide

## Overview

AutoWallpaper now includes both CLI and GUI interfaces! Choose whichever you prefer.

## Launching the GUI

```bash
python gui_main.py
```

Or if you're in the project directory:
```bash
python gui_main.py
```

## GUI Features

### 🎨 Intuitive Interface
- Clean, organized layout
- Dropdown menus for easy selection
- Real-time updates
- Status indicators

### 📱 Provider Selection
- Select from 4 image providers
- See provider description (rate limits, API key requirements)
- Automatic category and mood updates based on provider

### 📂 Category Selection
- Dynamic category list updates based on selected provider
- All available categories for each provider
- Easy dropdown selection

### 🎨 Mood Filter (Optional)
- Optional mood/style filters where available
- Some providers (waifu.im, nekos.moe) don't support moods
- "None" option to skip mood filtering

### 📐 Resolution Selection
- 5 preset resolutions
  - 1920x1080 (HD)
  - 1366x768 (Common laptop)
  - 1280x720 (720p)
  - 2560x1440 (2K)
  - 3840x2160 (4K)

### ⬇️ Download & Set
- Single-click wallpaper download and setting
- Progress indicator during download
- Status updates showing what's happening
- Error messages if something goes wrong

### ⏳ Non-blocking Download
- Download happens in background thread
- GUI remains responsive while downloading
- Progress bar shows activity
- Can't start another download while one is in progress

## How to Use

1. **Launch the GUI**
   ```bash
   python gui_main.py
   ```

2. **Select a Provider**
   - Click the "Image Provider" dropdown
   - Choose from: Pexels, Pixabay, waifu.im, nekos.moe
   - See the provider description below

3. **Select a Category**
   - Click the "Category" dropdown
   - Categories update based on your provider choice
   - Select your desired category

4. **Select a Mood (Optional)**
   - Click the "Mood" dropdown
   - Choose a mood or select "None" to skip
   - Some providers don't support moods

5. **Select a Resolution**
   - Click the "Resolution" dropdown
   - Choose your screen resolution
   - Or use default 1920x1080

6. **Download & Set**
   - Click "⬇️ Download & Set Wallpaper" button
   - Watch the status bar for progress
   - Wallpaper automatically sets when complete

## Provider Tips

### 🟢 Pexels
- No API key required
- 200 requests/hour limit
- Great for photography and real-world images

### 🟠 Pixabay
- **Requires API key**: `export PIXABAY_API_KEY='your-key'`
- 100 requests/hour limit
- Diverse images and illustrations

### 💜 waifu.im
- No API key required
- Unlimited requests
- Anime and waifu images

### 🐱 nekos.moe
- No API key required
- Unlimited requests
- Catgirl and anime characters

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next field |
| `Shift+Tab` | Move to previous field |
| `Enter` | Activate dropdown / click button |
| `Alt+D` | Click Download button |

## Status Messages

| Message | Meaning |
|---------|---------|
| ✅ Ready | Waiting for you to start download |
| ⏳ Downloading... | Fetching image from provider |
| 💾 Saving image... | Saving to disk |
| 🎨 Setting wallpaper... | Setting as desktop background |
| ✅ Ready | Download complete, ready for next |

## Error Handling

If something goes wrong:

### "Please select a provider!"
- Make sure a provider is selected in the dropdown
- Try selecting again

### "Please select a category!"
- Select a category from the dropdown
- Category list updates based on provider

### "Failed to set wallpaper..."
- Check error message for details
- On Linux: Make sure you have `feh`, `dconf-cli`, or `nitrogen` installed
- On Windows: Check permissions
- On macOS: Check Accessibility settings

## Window Features

### Resizable
- Drag window edges to resize
- All elements scale proportionally

### Responsive
- Download happens in background
- GUI never freezes
- Can view status while downloading

### Status Indication
- Progress bar shows activity
- Status text shows current step
- Color coding (green = ready, blue = tip)

## Comparison: CLI vs GUI

| Feature | CLI | GUI |
|---------|-----|-----|
| **Startup Time** | Fast | Fast |
| **User-Friendly** | Menus | Dropdowns |
| **Visual Feedback** | Text | Progress bar |
| **Required Skills** | Terminal comfort | None |
| **Automation** | Easy (scripts) | Not ideal |
| **Batch Operations** | Yes | Single download |

## Troubleshooting

### GUI doesn't open
```bash
# Make sure tkinter is installed
python -m tkinter  # Should show a test window

# If not installed (rare on modern Python):
# Ubuntu/Debian:
sudo apt install python3-tk

# macOS:
brew install python-tk

# Windows:
# Usually comes with Python, try reinstalling Python
```

### Download button is grayed out
- Another download is in progress
- Wait for the current download to complete

### Provider dropdown empty
- This shouldn't happen, but try:
  - Restart the application
  - Check that providers.py and config.py exist

### Status bar stuck at "Downloading..."
- Check internet connection
- Try again
- Check error message that should appear

## Advanced: Customizing the GUI

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for how to add new providers. They automatically appear in the GUI dropdown!

### Adding Custom Colors
Edit the `style` configuration in `gui.py`:
```python
self.style = ttk.Style()
self.style.theme_use('clam')  # Change to 'alt', 'default', 'clam'
```

## Performance Notes

- **First launch**: May take 1-2 seconds to import modules
- **Download time**: Depends on image size and internet speed
  - Usually 1-5 seconds
  - Very large 4K images may take longer
- **Memory**: Minimal (under 50MB typical)
- **CPU**: Low usage except during download

## Frequently Asked Questions

### Q: Can I run both CLI and GUI?
**A:** Yes! They're independent:
- `python main.py` → CLI (interactive terminal)
- `python gui_main.py` → GUI (window)

### Q: Can I schedule automatic downloads?
**A:** The GUI isn't ideal for automation. Use the CLI with a cron job instead (Linux/macOS) or Task Scheduler (Windows).

### Q: Does the GUI support multiple monitors?
**A:** Yes, the wallpaper setter uses your default monitor settings.

### Q: Can I use the GUI on a remote server?
**A:** Only if you have X11 forwarding or remote desktop. The CLI is better for servers.

### Q: Where are wallpapers saved?
**A:** 
- Windows: `%APPDATA%\Roaming\easy-wallpaper\`
- macOS: `~/.easy-wallpaper/`
- Linux: `~/.easy-wallpaper/`

## Tips & Tricks

### Save Your Favorites
1. Set a wallpaper you like
2. The file is saved to `~/.easy-wallpaper/wallpaper.png`
3. Copy it somewhere safe
4. Use file manager to set it whenever you want

### Try Random Selections
- Select different categories
- Click download multiple times
- Find new favorites!

### Use with Desktop Shortcuts
- Create a .desktop file (Linux) or .bat file (Windows) to launch
- Add to desktop for one-click wallpaper downloads

### Batch Processing
For multiple downloads, use the CLI:
```bash
# Script that downloads 10 random wallpapers
for i in {1..10}; do
    python main.py < auto_input.txt
done
```

---

**Enjoy downloading beautiful wallpapers with the GUI!** 🎨✨
