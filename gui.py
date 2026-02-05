import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import os
from processor import ImageProcessor

class ImageDisplay:
    """
    Class responsible for displaying images in the GUI.
    
    Handles resizing, aspect ratio preservation, and conversion 
    from OpenCV/NumPy arrays to Tkinter-compatible PhotoImage objects.
    
    Attributes:
        canvas (tk.Canvas): The canvas widget where the image is drawn.
        max_width (int): Maximum allowable width for the displayed image.
        max_height (int): Maximum allowable height for the displayed image.
        photo_image (ImageTk.PhotoImage): Keeps a reference to prevent garbage collection.
    """
    
    def __init__(self, canvas, max_width=800, max_height=600):
        """
        Initialize the ImageDisplay.
        
        Args:
            canvas (tk.Canvas): Target canvas.
            max_width (int): Max width constraints.
            max_height (int): Max height constraints.
        """
        self.canvas = canvas
        self.max_width = max_width
        self.max_height = max_height
        self.photo_image = None
        
    def display_image(self, cv_image):
        """
        Convert OpenCV image to Tkinter format and display it on the canvas.
        
        Auto-scales the image to fit within max_width/max_height while maintaining aspect ratio.
        
        Args:
            cv_image (numpy.ndarray): The image to display (in BGR format).
        """
        if cv_image is None:
            return
        
        # Convert from BGR (OpenCV default) to RGB (screen standard)
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        # Calculate scaling factor to fit within display limits
        h, w = rgb_image.shape[:2]
        scale = min(self.max_width / w, self.max_height / h, 1.0)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize only if image is larger than the display area
        # (We generally avoid upscaling to prevent blurriness, unless requested via filter)
        if scale < 1.0:
            rgb_image = cv2.resize(rgb_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Convert to PIL Image and then to Tkinter PhotoImage
        pil_image = Image.fromarray(rgb_image)
        self.photo_image = ImageTk.PhotoImage(pil_image)
        
        # specific reference must be kept to photo_image to prevent GC
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(
            self.max_width // 2, 
            self.max_height // 2, 
            image=self.photo_image, 
            anchor=tk.CENTER
        )


class ImageProcessorApp:
    """
    Main application class that manages the GUI and coordinates components.
    
    Acts as the Controller in the MVC pattern, mediating between:
    - Model: ImageProcessor (logic)
    - View: ImageDisplay and Tkinter Widgets (GUI)
    """
    
    def __init__(self, root):
        """Initialize the main application window and components."""
        self.root = root
        self.root.title("Image Processor - Professional Edition")
        self.root.geometry("1200x800")
        
        # Initialize logic component
        self.processor = ImageProcessor()
        self.current_filepath = None
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        
        # Initialize display component
        self.display = ImageDisplay(self.canvas, max_width=800, max_height=600)
        
        # Bind window close event to ensure safe exit (check for unsaved changes)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
    def create_menu(self):
        """Create the top menu bar with File and Edit options."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_image_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset to Original", command=self.reset_image)
        
        # Keyboard shortcuts bindings
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-S>", lambda e: self.save_image_as()) # Shift+S usually comes as capital S
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        
    def create_main_layout(self):
        """Create the main application layout frames."""
        # Main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- Left Panel: Controls ---
        # Fixed width for controls
        left_panel = ttk.Frame(main_container, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False) # Prevent shrinking
        
        # Title for controls
        ttk.Label(left_panel, text="Image Processing Tools", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Scrollable Frame Implementation
        self.canvas_scroll = tk.Canvas(left_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.canvas_scroll.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas_scroll)
        
        # Bind inner frame configuration to update scrollregion
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
        )
        
        # Create window inside canvas
        self.frame_window = self.canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Ensure inner frame fills the canvas width
        self.canvas_scroll.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.itemconfig(self.frame_window, width=e.width)
        )
        
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        self.canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind MouseWheel for better UX
        self.bind_mousewheel(self.canvas_scroll)
        self.bind_mousewheel(self.scrollable_frame)
        
        # Add controls to the scrollable frame
        self.create_controls(self.scrollable_frame)
        
        # --- Right Panel: Image Display ---
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Dark background canvas for professional look
        self.canvas = tk.Canvas(right_panel, bg="gray25", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
    def bind_mousewheel(self, widget):
        """Bind mousewheel events to widget and its children for scrolling."""
        widget.bind("<Enter>", lambda _: self.canvas_scroll.bind_all("<MouseWheel>", self._on_mousewheel))
        widget.bind("<Leave>", lambda _: self.canvas_scroll.unbind_all("<MouseWheel>"))
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_controls(self, parent):
        """
        Create all control buttons and sliders in the scrollable control panel.
        
        Args:
            parent: The parent widget (scrollable_frame) to add controls to.
        """
        
        # Basic Filters Section
        filters_frame = ttk.LabelFrame(parent, text="Basic Filters", padding=10)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(filters_frame, text="Grayscale", 
                  command=self.apply_grayscale).pack(fill=tk.X, pady=2)
        ttk.Button(filters_frame, text="Edge Detection", 
                  command=self.apply_edge_detection).pack(fill=tk.X, pady=2)
        
        # Blur Section
        blur_frame = ttk.LabelFrame(parent, text="Blur Effect", padding=10)
        blur_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(blur_frame, text="Intensity:").pack()
        self.blur_slider = ttk.Scale(blur_frame, from_=1, to=15, orient=tk.HORIZONTAL)
        self.blur_slider.set(5)
        self.blur_slider.pack(fill=tk.X, pady=5)
        ttk.Button(blur_frame, text="Apply Blur", 
                  command=self.apply_blur).pack(fill=tk.X, pady=2)
        
        # Brightness Section
        brightness_frame = ttk.LabelFrame(parent, text="Brightness", padding=10)
        brightness_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(brightness_frame, text="Adjustment:").pack()
        self.brightness_slider = ttk.Scale(brightness_frame, from_=-100, to=100, 
                                          orient=tk.HORIZONTAL)
        self.brightness_slider.set(0)
        self.brightness_slider.pack(fill=tk.X, pady=5)
        ttk.Button(brightness_frame, text="Apply Brightness", 
                  command=self.apply_brightness).pack(fill=tk.X, pady=2)
        
        # Contrast Section
        contrast_frame = ttk.LabelFrame(parent, text="Contrast", padding=10)
        contrast_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(contrast_frame, text="Adjustment:").pack()
        self.contrast_slider = ttk.Scale(contrast_frame, from_=0.5, to=3.0, 
                                        orient=tk.HORIZONTAL)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X, pady=5)
        ttk.Button(contrast_frame, text="Apply Contrast", 
                  command=self.apply_contrast).pack(fill=tk.X, pady=2)
        
        # Rotation Section
        rotation_frame = ttk.LabelFrame(parent, text="Rotation", padding=10)
        rotation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(rotation_frame, text="Rotate 90°", 
                  command=lambda: self.rotate_image(90)).pack(fill=tk.X, pady=2)
        ttk.Button(rotation_frame, text="Rotate 180°", 
                  command=lambda: self.rotate_image(180)).pack(fill=tk.X, pady=2)
        ttk.Button(rotation_frame, text="Rotate 270°", 
                  command=lambda: self.rotate_image(270)).pack(fill=tk.X, pady=2)
        
        # Flip Section
        flip_frame = ttk.LabelFrame(parent, text="Flip", padding=10)
        flip_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(flip_frame, text="Flip Horizontal", 
                  command=lambda: self.flip_image("horizontal")).pack(fill=tk.X, pady=2)
        ttk.Button(flip_frame, text="Flip Vertical", 
                  command=lambda: self.flip_image("vertical")).pack(fill=tk.X, pady=2)
        
        # Resize Section
        resize_frame = ttk.LabelFrame(parent, text="Resize/Scale", padding=10)
        resize_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(resize_frame, text="Scale %:").pack()
        self.resize_slider = ttk.Scale(resize_frame, from_=10, to=200, 
                                      orient=tk.HORIZONTAL)
        self.resize_slider.set(100)
        self.resize_slider.pack(fill=tk.X, pady=5)
        ttk.Button(resize_frame, text="Apply Resize", 
                  command=self.resize_image).pack(fill=tk.X, pady=2)
        
    def create_status_bar(self):
        """Create status bar at bottom of window."""
        self.status_bar = ttk.Label(self.root, text="Ready | No image loaded", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_status(self):
        """Update status bar with the current filename and dimensions."""
        if self.current_filepath:
            filename = os.path.basename(self.current_filepath)
            info = self.processor.get_image_info()
            self.status_bar.config(text=f"{filename} | {info}")
        else:
            self.status_bar.config(text="Ready | No image loaded")
    
    def open_image(self):
        """Handle Open Image action."""
        filepath = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            try:
                self.processor.load_image(filepath)
                self.current_filepath = filepath
                self.display.display_image(self.processor.get_current_image())
                self.update_status()
                messagebox.showinfo("Success", "Image loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {str(e)}")
    
    def save_image(self):
        """Handle Save action (overwrites current file if exists, else Save As)."""
        if self.current_filepath:
            self.save_image_to_path(self.current_filepath)
        else:
            self.save_image_as()
    
    def save_image_as(self):
        """Handle Save As action."""
        if self.processor.current_image is None:
            messagebox.showwarning("Warning", "No image to save!")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            self.save_image_to_path(filepath)
            self.current_filepath = filepath
    
    def save_image_to_path(self, filepath):
        """
        Helper to save image to disk and update state.
        
        Args:
            filepath (str): Destination path.
        """
        try:
            cv2.imwrite(filepath, self.processor.current_image)
            self.processor.mark_saved()
            self.update_status()
            messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image: {str(e)}")
    
    def undo(self):
        """Trigger Undo action."""
        if self.processor.undo():
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def redo(self):
        """Trigger Redo action."""
        if self.processor.redo():
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def reset_image(self):
        """Trigger Reset action."""
        if self.processor.original_image is not None:
            confirm = messagebox.askyesno("Confirm Reset", 
                                         "Reset to original image? This will clear all edits.")
            if confirm:
                self.processor.reset_to_original()
                self.display.display_image(self.processor.get_current_image())
                self.update_status()
    
    # --- Wrapper methods for filters to check if image is loaded ---
    
    def apply_grayscale(self):
        if self.check_image_loaded():
            self.processor.convert_to_grayscale()
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def apply_blur(self):
        if self.check_image_loaded():
            intensity = int(self.blur_slider.get())
            self.processor.apply_blur(intensity)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def apply_edge_detection(self):
        if self.check_image_loaded():
            self.processor.detect_edges()
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def apply_brightness(self):
        if self.check_image_loaded():
            value = int(self.brightness_slider.get())
            self.processor.adjust_brightness(value)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
            self.brightness_slider.set(0) # Reset slider
    
    def apply_contrast(self):
        if self.check_image_loaded():
            value = self.contrast_slider.get()
            self.processor.adjust_contrast(value)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
            self.contrast_slider.set(1.0) # Reset slider
    
    def rotate_image(self, angle):
        if self.check_image_loaded():
            self.processor.rotate_image(angle)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def flip_image(self, direction):
        if self.check_image_loaded():
            self.processor.flip_image(direction)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def resize_image(self):
        if self.check_image_loaded():
            scale = int(self.resize_slider.get())
            
            if scale == 100:
                messagebox.showinfo("Resize", "Scale is 100%, no changes made.")
                return

            # Capture old dimensions for feedback
            old_h, old_w = self.processor.current_image.shape[:2]
            
            self.processor.resize_image(scale)
            
            # Capture new dimensions
            new_h, new_w = self.processor.current_image.shape[:2]
            
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
            
            self.resize_slider.set(100) # Reset slider
            
            messagebox.showinfo("Success", f"Image resized from {old_w}x{old_h} to {new_w}x{new_h}")

    
    def check_image_loaded(self):
        """Helper to check availability of image before processing."""
        if self.processor.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first!")
            return False
        return True
    
    def exit_app(self):
        """Handle app exit."""
        if self.processor.is_modified:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                               "You have unsaved changes. Save before closing?")
            if response is True:  # Yes - Save
                self.save_image()
                # Check if save was successful (unmodified)
                if not self.processor.is_modified:
                    self.root.quit()
            elif response is False:  # No - Discard
                self.root.quit()
        else:
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.root.quit()
