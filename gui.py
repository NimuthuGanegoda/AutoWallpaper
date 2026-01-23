"""
GUI interface for AutoWallpaper using tkinter.

Provides a user-friendly graphical interface for downloading and
setting wallpapers from various image providers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
from typing import Optional
from PIL import Image, ImageTk

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
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Current selected provider
        self.current_provider: Optional[ImageProvider] = None
        self.downloading = False
        self.preview_image = None
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Setup GUI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Create main grid container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)  # Left column
        main_container.columnconfigure(1, weight=1)  # Right column

        # --- LEFT COLUMN ---
        left_column = ttk.Frame(main_container)
        left_column.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_column.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            left_column,
            text="🖼️ AutoWallpaper",
            font=("Helvetica", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        # Settings Frame
        settings_frame = ttk.LabelFrame(left_column, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(0, weight=1)
        
        # Provider Selection
        ttk.Label(settings_frame, text="📱 Image Provider:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.provider_var = tk.StringVar()
        provider_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.provider_var,
            values=[p.get_name() for p in PROVIDERS.values()],
            state="readonly"
        )
        provider_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
        
        # Description label
        self.provider_desc = ttk.Label(settings_frame, text="", foreground="gray", wraplength=350)
        self.provider_desc.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Category Selection
        ttk.Label(settings_frame, text="📂 Category:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.category_var,
            state="readonly"
        )
        self.category_combo.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Mood Selection
        ttk.Label(settings_frame, text="🎨 Mood (Optional):").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.mood_var = tk.StringVar()
        self.mood_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.mood_var,
            values=["None"],
            state="readonly"
        )
        self.mood_combo.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.mood_combo.current(0)
        
        # Resolution Selection
        ttk.Label(settings_frame, text="📐 Resolution:").grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        self.resolution_var = tk.StringVar()
        resolution_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.resolution_var,
            values=RESOLUTIONS,
            state="readonly"
        )
        resolution_combo.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        resolution_combo.current(0)

        # Initialize provider (triggers events)
        provider_combo.current(0)
        self.on_provider_change()

        # Actions Frame
        actions_frame = ttk.LabelFrame(left_column, text="Actions", padding="10")
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        
        # Download Button
        self.download_button = ttk.Button(
            actions_frame,
            text="⬇️ Download & Set",
            command=self.on_download
        )
        self.download_button.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Randomize Button
        self.randomize_button = ttk.Button(
            actions_frame,
            text="🎲 Randomize Settings",
            command=self.on_randomize
        )
        self.randomize_button.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            actions_frame,
            mode="indeterminate"
        )
        self.progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            actions_frame,
            textvariable=self.status_var,
            foreground="green",
            justify=tk.CENTER
        )
        status_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Info frame
        info_frame = ttk.LabelFrame(left_column, text="Info", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        info_label = ttk.Label(
            info_frame,
            text="💡 Tip: waifu.im and nekos.moe don't require API keys!",
            foreground="blue",
            justify=tk.CENTER,
            wraplength=350
        )
        info_label.pack()

        # --- RIGHT COLUMN (Preview) ---
        right_column = ttk.Frame(main_container)
        right_column.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_column.columnconfigure(0, weight=1)
        right_column.rowconfigure(0, weight=1)

        preview_frame = ttk.LabelFrame(right_column, text="Preview", padding="10")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.preview_label = ttk.Label(preview_frame, text="No image downloaded yet")
        self.preview_label.pack(expand=True, fill=tk.BOTH)

    
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
                categories = CATEGORIES.get(provider_name, [])
                self.category_combo['values'] = categories
                if categories:
                    self.category_combo.current(0)
                
                # Update moods
                moods = MOODS.get(provider_name, [""])
                mood_list = [m for m in moods if m]
                if mood_list:
                    self.mood_combo['values'] = ["None"] + mood_list
                else:
                    self.mood_combo['values'] = ["None"]
                self.mood_combo.current(0)
                
                break
    
    def on_randomize(self):
        """Randomly select settings."""
        # Select random provider
        provider_keys = list(PROVIDERS.keys())
        random_key = random.choice(provider_keys)
        provider_name = PROVIDERS[random_key].get_name()
        self.provider_var.set(provider_name)
        self.on_provider_change()

        # Select random category
        categories = self.category_combo['values']
        if categories:
            random_category = random.choice(categories)
            self.category_var.set(random_category)

        # Select random mood (sometimes)
        moods = self.mood_combo['values']
        if len(moods) > 1:
            random_mood = random.choice(moods)
            self.mood_var.set(random_mood)

    def update_preview(self, image_path: str):
        """
        Update the preview label with the downloaded image.

        Args:
            image_path: Path to the image file.
        """
        try:
            img = Image.open(image_path)

            # Calculate resize dimensions
            display_width = 400
            display_height = 500

            # Preserve aspect ratio
            img_ratio = img.width / img.height
            display_ratio = display_width / display_height

            if img_ratio > display_ratio:
                # Width is limiting factor
                new_width = display_width
                new_height = int(display_width / img_ratio)
            else:
                # Height is limiting factor
                new_height = display_height
                new_width = int(display_height * img_ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)

            self.preview_label.config(image=self.tk_image, text="")
        except Exception as e:
            print(f"Error loading preview: {e}")
            self.preview_label.config(text="Error loading preview", image="")

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
        
        # Disable button and show progress
        self.download_button.config(state="disabled")
        self.randomize_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("⏳ Downloading...")
        self.downloading = True
        
        # Run download in separate thread to avoid freezing GUI
        thread = threading.Thread(
            target=self.download_wallpaper,
            args=(category, mood)
        )
        thread.daemon = True
        thread.start()
    
    def download_wallpaper(self, category: str, mood: str):
        """
        Download and set wallpaper in separate thread.
        
        Args:
            category: Image category
            mood: Optional mood filter
        """
        try:
            # Update status
            self.root.after(0, lambda: self.status_var.set("⏳ Downloading image..."))
            
            # Download image
            image_data = self.current_provider.download_image(category, mood)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("💾 Saving image..."))
            
            # Save wallpaper
            path = save_wallpaper(image_data)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("🎨 Setting wallpaper..."))
            
            # Set wallpaper
            set_wallpaper(path)
            
            # Update preview
            self.root.after(0, lambda: self.update_preview(path))

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
        self.randomize_button.config(state="normal")
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
