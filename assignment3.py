import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os


class ImageProcessor:
    """Class responsible for all image processing operations using OpenCV"""
    
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.history = []
        self.history_index = -1
        self.is_modified = False
        
    def load_image(self, filepath):
        """Load an image from file"""
        self.original_image = cv2.imread(filepath)
        if self.original_image is None:
            raise ValueError("Could not load image")
        self.current_image = self.original_image.copy()
        self.history = [self.current_image.copy()]
        self.history_index = 0
        self.is_modified = False
        return self.current_image
    
    def save_to_history(self):
        """Save current state to history for undo/redo"""
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_image.copy())
        self.history_index += 1
        self.is_modified = True
        if len(self.history) > 20:  # Limit history size
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        """Undo last operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.is_modified = True
            return True
        return False
    
    def redo(self):
        """Redo last undone operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.is_modified = True
            return True
        return False
    
    def convert_to_grayscale(self):
        """Convert image to grayscale"""
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
        self.save_to_history()
        
    def apply_blur(self, intensity):
        """Apply Gaussian blur with adjustable intensity"""
        kernel_size = max(1, intensity * 2 + 1)  # Ensure odd number
        self.current_image = cv2.GaussianBlur(self.current_image, (kernel_size, kernel_size), 0)
        self.save_to_history()
    
    def detect_edges(self, threshold1=100, threshold2=200):
        """Apply Canny edge detection"""
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1, threshold2)
        self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.save_to_history()
    
    def adjust_brightness(self, value):
        """Adjust image brightness (-100 to +100)"""
        hsv = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + value, 0, 255)
        self.current_image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        self.save_to_history()
    
    def adjust_contrast(self, value):
        """Adjust image contrast (0.5 to 3.0)"""
        self.current_image = cv2.convertScaleAbs(self.current_image, alpha=value, beta=0)
        self.save_to_history()
    
    def rotate_image(self, angle):
        """Rotate image by specified angle (90, 180, or 270 degrees)"""
        if angle == 90:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_180)
        elif angle == 270:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.save_to_history()
    
    def flip_image(self, direction):
        """Flip image horizontally or vertically"""
        if direction == "horizontal":
            self.current_image = cv2.flip(self.current_image, 1)
        elif direction == "vertical":
            self.current_image = cv2.flip(self.current_image, 0)
        self.save_to_history()
    
    def resize_image(self, scale_percent):
        """Resize image by percentage"""
        width = int(self.current_image.shape[1] * scale_percent / 100)
        height = int(self.current_image.shape[0] * scale_percent / 100)
        self.current_image = cv2.resize(self.current_image, (width, height), interpolation=cv2.INTER_AREA)
        self.save_to_history()
    
    def reset_to_original(self):
        """Reset to original image"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.save_to_history()
    
    def get_current_image(self):
        """Get current image"""
        return self.current_image
    
    def get_image_info(self):
        """Get information about current image"""
        if self.current_image is not None:
            h, w = self.current_image.shape[:2]
            return f"{w}x{h} pixels"
        return "No image loaded"
    
    def mark_saved(self):
        """Mark current state as saved"""
        self.is_modified = False


class ImageDisplay:
    """Class responsible for displaying images in the GUI"""
    
    def __init__(self, canvas, max_width=800, max_height=600):
        self.canvas = canvas
        self.max_width = max_width
        self.max_height = max_height
        self.photo_image = None
        
    def display_image(self, cv_image):
        """Convert OpenCV image to Tkinter format and display"""
        if cv_image is None:
            return
        
        # Convert from BGR to RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        # Resize for display while maintaining aspect ratio
        h, w = rgb_image.shape[:2]
        scale = min(self.max_width / w, self.max_height / h, 1.0)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        if scale < 1.0:
            rgb_image = cv2.resize(rgb_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Convert to PIL Image and then to PhotoImage
        pil_image = Image.fromarray(rgb_image)
        self.photo_image = ImageTk.PhotoImage(pil_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(
            self.max_width // 2, 
            self.max_height // 2, 
            image=self.photo_image, 
            anchor=tk.CENTER
        )


class ImageProcessorApp:
    """Main application class that manages the GUI and coordinates components"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor - Professional Edition")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.processor = ImageProcessor()
        self.current_filepath = None
        
        # Create GUI
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        
        # Initialize display
        # Initialize display
        self.display = ImageDisplay(self.canvas, max_width=800, max_height=600)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
    def create_menu(self):
        """Create menu bar"""
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
        
        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_image_as())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        
    def create_main_layout(self):
        """Create main application layout with a functional scrollbar"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Control panel
        left_panel = ttk.Frame(main_container, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False) # Prevents panel from shrinking
        
        # Control panel title
        ttk.Label(left_panel, text="Image Processing Tools", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # --- SCROLLABLE CANVAS SETUP ---
        self.ctrl_canvas = tk.Canvas(left_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.ctrl_canvas.yview)
        
        # The frame that actually holds the widgets
        scrollable_frame = ttk.Frame(self.ctrl_canvas)
        
        # 1. Capture the window ID to resize it later
        self.canvas_window = self.ctrl_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # 2. Update scrollregion when the frame size changes
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.ctrl_canvas.configure(scrollregion=self.ctrl_canvas.bbox("all"))
        )

        # 3. Force the frame to match the width of the canvas
        self.ctrl_canvas.bind(
            "<Configure>",
            lambda e: self.ctrl_canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.ctrl_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add mousewheel support
        self.ctrl_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.ctrl_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add controls to the frame
        self.create_controls(scrollable_frame)
        
        # Right panel - Image display
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(right_panel, bg="gray25", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _on_mousewheel(self, event):
        """Allows scrolling with the mouse wheel"""
        self.ctrl_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_controls(self, parent):
        """Create control buttons and sliders"""
        
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
        """Create status bar at bottom"""
        self.status_bar = ttk.Label(self.root, text="Ready | No image loaded", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_status(self):
        """Update status bar with current image info"""
        if self.current_filepath:
            filename = os.path.basename(self.current_filepath)
            info = self.processor.get_image_info()
            self.status_bar.config(text=f"{filename} | {info}")
        else:
            self.status_bar.config(text="Ready | No image loaded")
    
    def open_image(self):
        """Open image file dialog"""
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
        """Save current image"""
        if self.current_filepath:
            self.save_image_to_path(self.current_filepath)
        else:
            self.save_image_as()
    
    def save_image_as(self):
        """Save image with new filename"""
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
        """Save image to specified path"""
        try:
            cv2.imwrite(filepath, self.processor.current_image)
            self.processor.mark_saved()
            self.update_status()
            messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image: {str(e)}")
    
    def undo(self):
        """Undo last operation"""
        if self.processor.undo():
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def redo(self):
        """Redo last undone operation"""
        if self.processor.redo():
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def reset_image(self):
        """Reset to original image"""
        if self.processor.original_image is not None:
            confirm = messagebox.askyesno("Confirm Reset", 
                                         "Reset to original image? This will clear all edits.")
            if confirm:
                self.processor.reset_to_original()
                self.display.display_image(self.processor.get_current_image())
                self.update_status()
    
    def apply_grayscale(self):
        """Apply grayscale filter"""
        if self.check_image_loaded():
            self.processor.convert_to_grayscale()
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def apply_blur(self):
        """Apply blur effect"""
        if self.check_image_loaded():
            intensity = int(self.blur_slider.get())
            self.processor.apply_blur(intensity)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def apply_edge_detection(self):
        """Apply edge detection"""
        if self.check_image_loaded():
            self.processor.detect_edges()
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def apply_brightness(self):
        """Apply brightness adjustment"""
        if self.check_image_loaded():
            value = int(self.brightness_slider.get())
            self.processor.adjust_brightness(value)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
            self.brightness_slider.set(0)
    
    def apply_contrast(self):
        """Apply contrast adjustment"""
        if self.check_image_loaded():
            value = self.contrast_slider.get()
            self.processor.adjust_contrast(value)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
            self.contrast_slider.set(1.0)
    
    def rotate_image(self, angle):
        """Rotate image"""
        if self.check_image_loaded():
            self.processor.rotate_image(angle)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def flip_image(self, direction):
        """Flip image"""
        if self.check_image_loaded():
            self.processor.flip_image(direction)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
    
    def resize_image(self):
        """Resize image"""
        if self.check_image_loaded():
            scale = int(self.resize_slider.get())
            self.processor.resize_image(scale)
            self.display.display_image(self.processor.get_current_image())
            self.update_status()
            self.resize_slider.set(100)
    
    def check_image_loaded(self):
        """Check if image is loaded"""
        if self.processor.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first!")
            return False
        return True
    
    def exit_app(self):
        """Exit application with confirmation"""
        if self.processor.is_modified:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                               "You have unsaved changes. Save before closing?")
            if response is True:  # Yes - Save
                self.save_image()
                # Check if save was successful (file exists and is not modified)
                # Since save_image logic is a bit decoupled, we'll check modified flag
                if not self.processor.is_modified:
                    self.root.quit()
            elif response is False:  # No - Discard
                self.root.quit()
            # Cancel - modify nothing, stay open
        else:
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.root.quit()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()