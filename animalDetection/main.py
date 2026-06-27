"""
Animal Detection & Classification System
Entry point — launch the GUI application.
"""

import sys
import os

# Ensure project root is on the path so relative imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import customtkinter as ctk
except ImportError:
    print(
        "ERROR: customtkinter is not installed.\n"
        "Run:  pip install customtkinter"
    )
    sys.exit(1)

try:
    from detector.animal_detector import AnimalDetector
except ImportError as exc:
    print(f"ERROR: Could not load detector module: {exc}")
    sys.exit(1)

try:
    from gui.app import AnimalDetectionApp
except ImportError as exc:
    print(f"ERROR: Could not load GUI module: {exc}")
    sys.exit(1)


def main():
    """Initialise the model and launch the GUI."""
    print("Loading YOLOv8 model (may download on first run)…")
    try:
        detector = AnimalDetector()
    except Exception as exc:
        try:
            from tkinter import messagebox
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Model Load Error",
                f"Failed to load YOLOv8 model:\n{exc}\n\n"
                "Check your internet connection and try again.",
            )
            root.destroy()
        except Exception:
            print(f"FATAL: {exc}")
        sys.exit(1)

    print("Model loaded. Launching GUI…")
    app = AnimalDetectionApp(detector)
    app.mainloop()


if __name__ == "__main__":
    main()
