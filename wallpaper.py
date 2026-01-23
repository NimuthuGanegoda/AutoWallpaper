"""
Wallpaper setting functionality for easy-wallpaper.

Handles setting wallpapers on different operating systems:
- Windows (using Windows API)
- macOS (using osascript)
- Linux (using dconf, feh, or pcmanfm)
"""

import os
import platform
import subprocess
from pathlib import Path


def save_wallpaper(image_data: bytes, filename: str = "wallpaper.png") -> str:
    """
    Save downloaded image to wallpaper directory.
    
    Args:
        image_data: The image file content as bytes
        filename: Name to save the file as (default: wallpaper.png)
    
    Returns:
        str: Path to the saved wallpaper file
    
    Raises:
        RuntimeError: If save operation fails
    """
    # Determine wallpaper directory based on OS
    if platform.system() == "Windows":
        wallpaper_dir = Path.home() / "AppData" / "Roaming" / "easy-wallpaper"
    elif platform.system() == "Darwin":  # macOS
        wallpaper_dir = Path.home() / ".easy-wallpaper"
    else:  # Linux
        wallpaper_dir = Path.home() / ".easy-wallpaper"
    
    # Create directory if it doesn't exist
    wallpaper_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the file
    file_path = wallpaper_dir / filename
    try:
        with open(file_path, "wb") as f:
            f.write(image_data)
        print(f"💾 Wallpaper saved to: {file_path}")
        return str(file_path)
    except IOError as e:
        raise RuntimeError(f"❌ Failed to save wallpaper: {e}")


def set_wallpaper(image_path: str) -> None:
    """
    Set the wallpaper for the current operating system.
    
    Args:
        image_path: Path to the image file
    
    Raises:
        RuntimeError: If setting wallpaper fails
        NotImplementedError: If OS is not supported
    """
    system = platform.system()
    
    if system == "Windows":
        set_wallpaper_windows(image_path)
    elif system == "Darwin":
        set_wallpaper_macos(image_path)
    elif system == "Linux":
        set_wallpaper_linux(image_path)
    else:
        raise NotImplementedError(f"❌ Wallpaper setting not supported on {system}")


def set_wallpaper_windows(image_path: str) -> None:
    """
    Set wallpaper on Windows using ctypes and WinAPI.
    
    Args:
        image_path: Path to the image file
    
    Raises:
        RuntimeError: If operation fails
    """
    import ctypes
    from ctypes import wintypes
    
    try:
        # Get absolute path
        abs_path = os.path.abspath(image_path)
        
        # Use Windows API to set wallpaper
        user32 = ctypes.windll.user32
        
        # SPI_SETDESKWALLPAPER = 20
        # SPIF_UPDATEINIFILE = 0x01
        # SPIF_SENDWININICHANGE = 0x02
        SPI_SETDESKWALLPAPER = 20
        result = user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, abs_path, 3
        )
        
        if result:
            print(f"✅ Wallpaper set successfully!")
        else:
            raise RuntimeError("Failed to set wallpaper via WinAPI")
    
    except Exception as e:
        raise RuntimeError(f"❌ Failed to set wallpaper on Windows: {e}")


def set_wallpaper_macos(image_path: str) -> None:
    """
    Set wallpaper on macOS using osascript (AppleScript).
    
    Args:
        image_path: Path to the image file
    
    Raises:
        RuntimeError: If operation fails
    """
    try:
        abs_path = os.path.abspath(image_path)
        
        # AppleScript to set wallpaper
        script = f"""
            tell application "System Events"
                tell every desktop
                    set picture to "{abs_path}"
                end tell
            end tell
        """
        
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if result.returncode == 0:
            print("✅ Wallpaper set successfully!")
        else:
            raise RuntimeError(result.stderr)
    
    except subprocess.TimeoutExpired:
        raise RuntimeError("❌ osascript command timed out")
    except FileNotFoundError:
        raise RuntimeError("❌ osascript not found. Please check your macOS installation.")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to set wallpaper on macOS: {e}")


def set_wallpaper_linux(image_path: str) -> None:
    """
    Set wallpaper on Linux using available tools (dconf, feh, or pcmanfm).
    
    Tries multiple methods:
    1. dconf (GNOME, Cinnamon)
    2. feh (standalone X11)
    3. pcmanfm (XFCE, LXde)
    
    Args:
        image_path: Path to the image file
    
    Raises:
        RuntimeError: If all methods fail
    """
    abs_path = os.path.abspath(image_path)
    
    # Detect desktop environment
    desktop_env = os.getenv("XDG_CURRENT_DESKTOP", "").lower()
    
    # Try dconf (GNOME, Cinnamon)
    if "gnome" in desktop_env or "cinnamon" in desktop_env:
        try:
            # GNOME
            subprocess.run(
                [
                    "dconf",
                    "write",
                    "/org/gnome/desktop/background/picture-uri",
                    f"'file://{abs_path}'",
                ],
                capture_output=True,
                timeout=5,
            )
            subprocess.run(
                [
                    "dconf",
                    "write",
                    "/org/gnome/desktop/background/picture-uri-dark",
                    f"'file://{abs_path}'",
                ],
                capture_output=True,
                timeout=5,
            )
            print("✅ Wallpaper set successfully!")
            return
        except Exception:
            pass
    
    # Try feh (X11)
    try:
        subprocess.run(
            ["feh", "--bg-scale", abs_path],
            capture_output=True,
            timeout=5,
            check=True,
        )
        print("✅ Wallpaper set successfully!")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Try pcmanfm-desktop (XFCE, LXDe)
    try:
        subprocess.run(
            ["pcmanfm-desktop", "-w", abs_path],
            capture_output=True,
            timeout=5,
            check=True,
        )
        print("✅ Wallpaper set successfully!")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Try nitrogen (another common X11 wallpaper setter)
    try:
        subprocess.run(
            ["nitrogen", "--set-zoom-fill", abs_path],
            capture_output=True,
            timeout=5,
            check=True,
        )
        print("✅ Wallpaper set successfully!")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    raise RuntimeError(
        f"❌ Failed to set wallpaper on Linux.\n"
        f"Please install one of: dconf, feh, pcmanfm-desktop, or nitrogen\n"
        f"Desktop environment detected: {desktop_env if desktop_env else 'Unknown'}"
    )
