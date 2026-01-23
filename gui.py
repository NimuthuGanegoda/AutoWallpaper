"""
GUI interface for AutoWallpaper using tkinter.

Provides a user-friendly graphical interface for downloading and
setting wallpapers from various image providers.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
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
        self.root.title("AutoWallpaper")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Current selected provider
        self.current_provider: Optional[ImageProvider] = None
        self.downloading = False
        self.preview_image = None
        
        # Setup styles first
        self.setup_styles()
        
        # Setup GUI elements
        self.setup_ui()
    
    def setup_styles(self):
        """Configure the custom styles for the Apple-like theme."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Colors
        BG_COLOR = "#F5F5F7"      # Apple light gray background
        CARD_COLOR = "#FFFFFF"    # White card background
        TEXT_COLOR = "#1D1D1F"    # Almost black text
        SUBTEXT_COLOR = "#86868B" # Gray subtext
        ACCENT_COLOR = "#0071E3"  # Apple Blue
        ACCENT_HOVER = "#0077ED"  # Slightly lighter blue

        # Configure root background
        self.root.configure(bg=BG_COLOR)

        # Fonts
        # Try to use San Francisco if available, else Helvetica/Arial
        available_fonts = font.families()
        if "San Francisco" in available_fonts:
            base_font = "San Francisco"
        elif "Helvetica Neue" in available_fonts:
            base_font = "Helvetica Neue"
        elif "Helvetica" in available_fonts:
            base_font = "Helvetica"
        else:
            base_font = "Arial"

        HEADER_FONT = (base_font, 24, "bold")
        TITLE_FONT = (base_font, 13, "bold")
        BODY_FONT = (base_font, 11)
        BUTTON_FONT = (base_font, 12)
        SMALL_FONT = (base_font, 10)

        # --- Configure Styles ---

        # Main container style
        self.style.configure("Main.TFrame", background=BG_COLOR)

        # Card style (White container with clean look)
        # We can't do rounded corners easily in pure Tkinter, but we can make it look clean
        self.style.configure("Card.TFrame",
            background=CARD_COLOR,
            relief="flat",
            borderwidth=0
        )

        # Labels
        self.style.configure("TLabel",
            background=CARD_COLOR,
            foreground=TEXT_COLOR,
            font=BODY_FONT
        )
        self.style.configure("Header.TLabel",
            background=BG_COLOR,
            foreground=TEXT_COLOR,
            font=HEADER_FONT
        )
        self.style.configure("CardTitle.TLabel",
            background=CARD_COLOR,
            foreground=TEXT_COLOR,
            font=TITLE_FONT
        )
        self.style.configure("Subtext.TLabel",
            background=CARD_COLOR,
            foreground=SUBTEXT_COLOR,
            font=SMALL_FONT
        )
        self.style.configure("Info.TLabel",
            background=BG_COLOR,
            foreground=SUBTEXT_COLOR,
            font=SMALL_FONT
        )

        # Buttons
        self.style.configure("Action.TButton",
            background=ACCENT_COLOR,
            foreground="white",
            font=BUTTON_FONT,
            borderwidth=0,
            focuscolor=BG_COLOR
        )
        self.style.map("Action.TButton",
            background=[('active', ACCENT_HOVER), ('pressed', ACCENT_HOVER)]
        )

        # Secondary Button (Randomize)
        self.style.configure("Secondary.TButton",
            background="#E8E8ED",
            foreground=TEXT_COLOR,
            font=BUTTON_FONT,
            borderwidth=0,
            focuscolor=BG_COLOR
        )
        self.style.map("Secondary.TButton",
            background=[('active', "#D2D2D7")]
        )

        # Combobox
        self.style.configure("TCombobox",
            fieldbackground=CARD_COLOR,
            background=CARD_COLOR,
            arrowcolor=TEXT_COLOR,
            relief="flat",
            padding=5
        )
        self.style.map("TCombobox",
            fieldbackground=[('readonly', CARD_COLOR)],
            selectbackground=[('readonly', CARD_COLOR)],
            selectforeground=[('readonly', TEXT_COLOR)]
        )

        # Progressbar
        self.style.configure("Horizontal.TProgressbar",
            background=ACCENT_COLOR,
            troughcolor="#E8E8ED",
            thickness=4,
            borderwidth=0
        )

    def setup_ui(self):
        """Setup the user interface."""
        # Main container with padding
        main_container = ttk.Frame(self.root, style="Main.TFrame", padding="40")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=4)  # Left column (Settings)
        main_container.columnconfigure(1, weight=5)  # Right column (Preview)

        # --- LEFT COLUMN ---
        left_column = ttk.Frame(main_container, style="Main.TFrame")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        left_column.columnconfigure(0, weight=1)
        
        # Header
        header_label = ttk.Label(
            left_column,
            text="AutoWallpaper",
            style="Header.TLabel"
        )
        header_label.grid(row=0, column=0, pady=(0, 30), sticky="w")

        # Settings Card
        settings_card = ttk.Frame(left_column, style="Card.TFrame", padding="25")
        settings_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        settings_card.columnconfigure(0, weight=1)

        # Card Title
        ttk.Label(settings_card, text="Settings", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Provider Selection
        ttk.Label(settings_card, text="Image Provider").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.provider_var = tk.StringVar()
        provider_combo = ttk.Combobox(
            settings_card,
            textvariable=self.provider_var,
            values=[p.get_name() for p in PROVIDERS.values()],
            state="readonly",
            height=8
        )
        provider_combo.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
        
        # Description
        self.provider_desc = ttk.Label(settings_card, text="", style="Subtext.TLabel", wraplength=300)
        self.provider_desc.grid(row=3, column=0, sticky="w", pady=(0, 15))
        
        # Category Selection
        ttk.Label(settings_card, text="Category").grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            settings_card,
            textvariable=self.category_var,
            state="readonly"
        )
        self.category_combo.grid(row=5, column=0, sticky="ew", pady=(0, 15))

        # Mood & Resolution in a sub-grid
        sub_grid = ttk.Frame(settings_card, style="Card.TFrame")
        sub_grid.grid(row=6, column=0, sticky="ew")
        sub_grid.columnconfigure(0, weight=1)
        sub_grid.columnconfigure(1, weight=1)
        
        # Mood
        ttk.Label(sub_grid, text="Mood").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.mood_var = tk.StringVar()
        self.mood_combo = ttk.Combobox(
            sub_grid,
            textvariable=self.mood_var,
            values=["None"],
            state="readonly"
        )
        self.mood_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        self.mood_combo.current(0)
        
        # Resolution
        ttk.Label(sub_grid, text="Resolution").grid(row=0, column=1, sticky="w", pady=(0, 5))
        self.resolution_var = tk.StringVar()
        resolution_combo = ttk.Combobox(
            sub_grid,
            textvariable=self.resolution_var,
            values=RESOLUTIONS,
            state="readonly"
        )
        resolution_combo.grid(row=1, column=1, sticky="ew", pady=(0, 10))
        resolution_combo.current(0)

        # Initialize provider
        provider_combo.current(0)
        self.on_provider_change()

        # Actions Card
        actions_card = ttk.Frame(left_column, style="Card.TFrame", padding="25")
        actions_card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        actions_card.columnconfigure(0, weight=1)
        
        # Download Button
        self.download_button = ttk.Button(
            actions_card,
            text="Download & Set Wallpaper",
            style="Action.TButton",
            command=self.on_download
        )
        self.download_button.grid(row=0, column=0, sticky="ew", pady=(0, 10), ipady=5)

        # Randomize Button
        self.randomize_button = ttk.Button(
            actions_card,
            text="Randomize Settings",
            style="Secondary.TButton",
            command=self.on_randomize
        )
        self.randomize_button.grid(row=1, column=0, sticky="ew", pady=(0, 15), ipady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            actions_card,
            mode="indeterminate",
            style="Horizontal.TProgressbar"
        )
        self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            actions_card,
            textvariable=self.status_var,
            style="Subtext.TLabel",
            justify=tk.CENTER
        )
        status_label.grid(row=3, column=0, sticky="ew")
        
        # Info
        info_label = ttk.Label(
            left_column,
            text="Tip: Some providers like waifu.im support unlimited free downloads.",
            style="Info.TLabel",
            justify=tk.LEFT,
            wraplength=350
        )
        info_label.grid(row=3, column=0, sticky="w", padx=5)

        # --- RIGHT COLUMN (Preview) ---
        right_column = ttk.Frame(main_container, style="Main.TFrame")
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.columnconfigure(0, weight=1)
        right_column.rowconfigure(1, weight=1)

        ttk.Label(right_column, text="Preview", style="CardTitle.TLabel", background="#F5F5F7").grid(row=0, column=0, sticky="w", pady=(0, 15))

        preview_card = ttk.Frame(right_column, style="Card.TFrame", padding="0")
        preview_card.grid(row=1, column=0, sticky="nsew")

        # Inner frame to center image content
        preview_inner = ttk.Frame(preview_card, style="Card.TFrame")
        preview_inner.pack(expand=True, fill="both", padx=10, pady=10)

        self.preview_label = ttk.Label(preview_inner, text="No image selected", style="Subtext.TLabel")
        self.preview_label.pack(expand=True)

    
    def on_provider_change(self, event=None):
        """Handle provider selection change."""
        provider_name = self.provider_var.get()
        
        # Find the provider instance
        for provider in PROVIDERS.values():
            if provider.get_name() == provider_name:
                self.current_provider = provider
                
                # Update description
                self.provider_desc.config(text=provider.get_description())
                
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

    def _resize_image_for_preview(self, image_path: str) -> Optional[Image.Image]:
        """
        Resize image for preview in background thread.

        Args:
            image_path: Path to image file

        Returns:
            Resized PIL Image or None on error
        """
        try:
            img = Image.open(image_path)

            # Calculate resize dimensions
            display_width = 500
            display_height = 600

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

            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Error resizing preview: {e}")
            return None

    def _set_preview_image(self, img: Image.Image):
        """
        Set the preview image on the main thread.

        Args:
            img: PIL Image object
        """
        self.tk_image = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.tk_image, text="")

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
        self.status_var.set("Downloading...")
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
            self.root.after(0, lambda: self.status_var.set("Downloading image..."))
            
            # Download image
            image_data = self.current_provider.download_image(category, mood)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("Saving image..."))
            
            # Save wallpaper
            path = save_wallpaper(image_data)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("Setting wallpaper..."))
            
            # Set wallpaper
            set_wallpaper(path)
            
            # Resize image in background thread
            resized_img = self._resize_image_for_preview(path)

            # Update preview on main thread
            if resized_img:
                self.root.after(0, lambda: self._set_preview_image(resized_img))
            else:
                self.root.after(0, lambda: self.preview_label.config(text="Error loading preview", image=""))

            # Success!
            self.root.after(
                0,
                lambda: self.show_success(f"Wallpaper set successfully!")
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
        self.status_var.set("Ready")
    
    def show_success(self, message: str):
        """Show success message."""
        messagebox.showinfo("Success", message)


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = AutoWallpaperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
