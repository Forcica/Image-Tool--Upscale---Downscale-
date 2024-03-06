import tkinter as tk
from upscale_image_source.gui import ImageToolApp  # Import modifié

def main():
    root = tk.Tk()
    app = ImageToolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
