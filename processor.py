import cv2
import numpy as np

class ImageProcessor:
    """
    Class responsible for all image processing operations using OpenCV.
    
    Attributes:
        original_image (numpy.ndarray): Stores the originally loaded image.
        current_image (numpy.ndarray): Stores the currently processed image.
        history (list): Stack of images for undo/redo functionality.
        history_index (int): Current position in the history stack.
        is_modified (bool): Flag to track if unsaved changes exist.
    """
    
    def __init__(self):
        """Initialize the ImageProcessor with default values."""
        self.original_image = None
        self.current_image = None
        self.history = []
        self.history_index = -1
        self.is_modified = False
        
    def load_image(self, filepath):
        """
        Load an image from the specified file path.
        
        Args:
            filepath (str): Path to the image file.
            
        Returns:
            numpy.ndarray: The loaded image.
            
        Raises:
            ValueError: If the image cannot be loaded.
        """
        self.original_image = cv2.imread(filepath)
        if self.original_image is None:
            raise ValueError("Could not load image")
        
        # Create a copy for processing to preserve the original
        self.current_image = self.original_image.copy()
        
        # Initialize history with the loaded image
        self.history = [self.current_image.copy()]
        self.history_index = 0
        self.is_modified = False
        return self.current_image
    
    def save_to_history(self):
        """
        Save the current image state to the history stack.
        
        This manages the undo/redo stack, removing any 'redo' paths
        if a new action is taken, and limits the history size to 20 steps.
        """
        # Truncate history if we are in the middle of the stack (after undoing)
        self.history = self.history[:self.history_index + 1]
        
        # Append current state
        self.history.append(self.current_image.copy())
        self.history_index += 1
        self.is_modified = True
        
        # Maintain a maximum history limit to save memory
        if len(self.history) > 20:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        """
        Revert the current image to the previous state in history.
        
        Returns:
            bool: True if undo was successful (history existed), False otherwise.
        """
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.is_modified = True
            return True
        return False
    
    def redo(self):
        """
        Reapply the next state in history if it exists.
        
        Returns:
            bool: True if redo was successful, False otherwise.
        """
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.is_modified = True
            return True
        return False
    
    def convert_to_grayscale(self):
        """
        Convert the current image to grayscale.
        
        We convert to Gray and then back to BGR to maintain the 3-channel structure
        expected by other OpenCV functions and the GUI display.
        """
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
        self.save_to_history()
        
    def apply_blur(self, intensity):
        """
        Apply Gaussian blur to the image.
        
        Args:
            intensity (int): The magnitude of the blur.
        """
        # Kernel size must be an odd positive integer
        kernel_size = max(1, intensity * 2 + 1)
        self.current_image = cv2.GaussianBlur(self.current_image, (kernel_size, kernel_size), 0)
        self.save_to_history()
    
    def detect_edges(self, threshold1=100, threshold2=200):
        """
        Apply Canny edge detection to the image.
        
        Args:
            threshold1 (int): First threshold for the hysteresis procedure.
            threshold2 (int): Second threshold for the hysteresis procedure.
        """
        # Canny requires a grayscale image
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1, threshold2)
        
        # Convert back to BGR for consistency
        self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.save_to_history()
    
    def adjust_brightness(self, value):
        """
        Adjust the brightness of the image.
        
        Args:
            value (int): Brightness offset (-100 to +100).
        """
        # Convert to HSV color space to adjust Value (Brightness) channel
        hsv = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Add offset and clip values to valid range [0, 255]
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + value, 0, 255)
        
        # Convert back to BGR
        self.current_image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        self.save_to_history()
    
    def adjust_contrast(self, value):
        """
        Adjust the contrast of the image.
        
        Args:
            value (float): Contrast multiplier (e.g., 1.0 is original, >1 increases contrast).
        """
        # Use convertScaleAbs for optimized linear transformation
        self.current_image = cv2.convertScaleAbs(self.current_image, alpha=value, beta=0)
        self.save_to_history()
    
    def rotate_image(self, angle):
        """
        Rotate the image by a fixed angle (90, 180, 270).
        
        Args:
            angle (int): The angle to rotate (degrees).
        """
        if angle == 90:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_180)
        elif angle == 270:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.save_to_history()
    
    def flip_image(self, direction):
        """
        Flip the image horizontally or vertically.
        
        Args:
            direction (str): 'horizontal' or 'vertical'.
        """
        if direction == "horizontal":
            self.current_image = cv2.flip(self.current_image, 1) # 1 = horizontal
        elif direction == "vertical":
            self.current_image = cv2.flip(self.current_image, 0) # 0 = vertical
        self.save_to_history()
    
    def resize_image(self, scale_percent):
        """
        Resize the image by a percentage scale.
        
        Args:
            scale_percent (int): The percentage to scale to (e.g., 50 for half size).
        """
        # Calculate new dimensions
        width = int(self.current_image.shape[1] * scale_percent / 100)
        height = int(self.current_image.shape[0] * scale_percent / 100)
        
        # Ensure dimensions are at least 1x1 to prevent errors
        width = max(1, width)
        height = max(1, height)
        
        # Select appropriate interpolation:
        # Cubic looks better for enlargement (>100%), Area is better/moiré-free for shrinking (<100%)
        if scale_percent > 100:
            interpolation = cv2.INTER_CUBIC
        else:
            interpolation = cv2.INTER_AREA
            
        self.current_image = cv2.resize(self.current_image, (width, height), interpolation=interpolation)
        self.save_to_history()
    
    def reset_to_original(self):
        """Discard all changes and revert to the originally loaded image."""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.save_to_history()
    
    def get_current_image(self):
        """Return the current processing image."""
        return self.current_image
    
    def get_image_info(self):
        """Returns a string describing the current image dimensions."""
        if self.current_image is not None:
            h, w = self.current_image.shape[:2]
            return f"{w}x{h} pixels"
        return "No image loaded"
    
    def mark_saved(self):
        """Mark the current application state as saved (unmodified)."""
        self.is_modified = False
