import tkinter as tk
from gui import ImageProcessorApp

def main():
    """
    Main entry point for the Image Processing Application.
    
    Initializes the root Tkinter window and starts the application loop.
    """
    root = tk.Tk()
    
    # Create the application instance with the root window
    app = ImageProcessorApp(root)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()

