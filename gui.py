"""
GUI interface for AutoWallpaper using tkinter.

Provides a user-friendly graphical interface for downloading and
setting wallpapers from various image providers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from providers import ImageProvider
from config import PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS
from wallpaper import save_wallpaper, set_wallpaper


class AutoWallpaperGUI:
    """Main GUI window for AutoWallpaper application."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI.
        
        Args:
            root: tkinter root window
        """
        self.root = root
        self.root.title("🖼️ AutoWallpaper")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Current selected provider
        self.current_provider: Optional[ImageProvider] = None
        self.downloading = False
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Setup GUI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🖼️ AutoWallpaper",
            font=("Helvetica", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # NSFW Toggle
        self.nsfw_var = tk.BooleanVar(value=False)
        nsfw_check = ttk.Checkbutton(
            main_frame,
            text="🔞 Allow NSFW Content",
            variable=self.nsfw_var,
            command=self.on_nsfw_change
        )
        nsfw_check.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        # Provider Selection
        self.add_section(main_frame, "📱 Image Provider", 2)
        self.provider_var = tk.StringVar()
        provider_combo = ttk.Combobox(
            main_frame,
            textvariable=self.provider_var,
            values=[p.get_name() for p in PROVIDERS.values()],
            state="readonly",
            width=40
        )
        provider_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
        provider_combo.current(0)
        self.on_provider_change()
        
        # Description label
        self.provider_desc = ttk.Label(main_frame, text="", foreground="gray")
        self.provider_desc.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Category Selection
        self.add_section(main_frame, "📂 Category", 5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            state="readonly",
            width=40
        )
        self.category_combo.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Mood Selection
        self.add_section(main_frame, "🎨 Mood (Optional)", 7)
        self.mood_var = tk.StringVar()
        self.mood_combo = ttk.Combobox(
            main_frame,
            textvariable=self.mood_var,
            values=["None"],
            state="readonly",
            width=40
        )
        self.mood_combo.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.mood_combo.current(0)
        
        # Resolution Selection
        self.add_section(main_frame, "📐 Resolution", 9)
        self.resolution_var = tk.StringVar()
        resolution_combo = ttk.Combobox(
            main_frame,
            textvariable=self.resolution_var,
            values=RESOLUTIONS,
            state="readonly",
            width=40
        )
        resolution_combo.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        resolution_combo.current(0)
        
        # Download Button
        self.download_button = ttk.Button(
            main_frame,
            text="⬇️  Download & Set Wallpaper",
            command=self.on_download
        )
        self.download_button.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode="indeterminate",
            length=400
        )
        self.progress.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground="green",
            justify=tk.CENTER
        )
        status_label.grid(row=13, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Info frame at bottom
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=14, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
        info_label = ttk.Label(
            info_frame,
            text="💡 Tip: waifu.im and nekos.moe don't require API keys!",
            foreground="blue",
            justify=tk.CENTER
        )
        info_label.pack()
    
    def add_section(self, parent: ttk.Frame, title: str, row: int):
        """Add a section header."""
        section_label = ttk.Label(
            parent,
            text=title,
            font=("Helvetica", 12, "bold")
        )
        section_label.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
    
    def on_nsfw_change(self):
        """Handle NSFW toggle change."""
        # Refresh categories based on new NSFW setting
        self.on_provider_change()

    def on_provider_change(self, event=None):
        """Handle provider selection change."""
        provider_name = self.provider_var.get()
        
        # Find the provider instance
        for provider in PROVIDERS.values():
            if provider.get_name() == provider_name:
                self.current_provider = provider
                
                # Update description
                self.provider_desc.config(text=f"ℹ️  {provider.get_description()}")
                
                # Update categories
                all_categories = CATEGORIES.get(provider_name, [])

                # Filter categories if nekos.moe and NSFW disabled
                categories = []
                if provider_name == "nekos.moe":
                    nsfw_allowed = self.nsfw_var.get()
                    for cat in all_categories:
                        if not nsfw_allowed and (cat == "nsfw" or cat == "mixed"):
                            continue
                        categories.append(cat)
                else:
                    categories = all_categories

                self.category_combo['values'] = categories
                if categories:
                    self.category_combo.current(0)
                else:
                    self.category_combo.set('')
                
                # Update moods
                moods = MOODS.get(provider_name, [""])
                mood_list = [m for m in moods if m]
                if mood_list:
                    self.mood_combo['values'] = ["None"] + mood_list
                else:
                    self.mood_combo['values'] = ["None"]
                self.mood_combo.current(0)
                
                break
    
    def on_download(self):
        """Handle download button click."""
        if self.downloading:
            messagebox.showwarning("In Progress", "Download already in progress!")
            return
        
        if not self.current_provider:
            messagebox.showerror("Error", "Please select a provider!")
            return
        
        if not self.category_var.get():
            messagebox.showerror("Error", "Please select a category!")
            return
        
        # Get values
        category = self.category_var.get()
        mood = self.mood_var.get()
        mood = mood if mood != "None" else ""
        nsfw = self.nsfw_var.get()
        
        # Disable button and show progress
        self.download_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("⏳ Downloading...")
        self.status_var.set("⏳ Downloading...")
        self.downloading = True
        
        # Run download in separate thread to avoid freezing GUI
        thread = threading.Thread(
            target=self.download_wallpaper,
            args=(category, mood, nsfw)
        )
        thread.daemon = True
        thread.start()
    
    def download_wallpaper(self, category: str, mood: str, nsfw: bool):
        """
        Download and set wallpaper in separate thread.
        
        Args:
            category: Image category
            mood: Optional mood filter
            nsfw: Whether to allow NSFW content
        """
        try:
            # Update status
            self.root.after(0, lambda: self.status_var.set("⏳ Downloading image..."))
            
            # Download image
            image_data = self.current_provider.download_image(category, mood, nsfw=nsfw)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("💾 Saving image..."))
            
            # Save wallpaper
            path = save_wallpaper(image_data)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("🎨 Setting wallpaper..."))
            
            # Set wallpaper
            set_wallpaper(path)
            
            # Success!
            self.root.after(
                0,
                lambda: self.show_success(f"Wallpaper set successfully!\n{category}")
            )
        
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", f"Failed to set wallpaper:\n\n{str(e)}")
            )
        
        finally:
            # Re-enable button and hide progress
            self.root.after(0, self.on_download_complete)
    
    def on_download_complete(self):
        """Called when download is complete."""
        self.download_button.config(state="normal")
        self.progress.stop()
        self.downloading = False
        self.status_var.set("✅ Ready")
    
    def show_success(self, message: str):
        """Show success message."""
        messagebox.showinfo("Success!", f"✨ {message}")


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = AutoWallpaperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
