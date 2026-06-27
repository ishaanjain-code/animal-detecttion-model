"""
Image Detection Tab for the Animal Detection & Classification System.
"""

try:
    import customtkinter as ctk
except ImportError:
    raise ImportError(
        "customtkinter not found. Install with: pip install customtkinter"
    )

try:
    from tkinter import filedialog, messagebox
    import tkinter as tk
except ImportError:
    raise ImportError("tkinter not available — ensure you have a full Python install.")

from PIL import Image

import os

from utils.image_utils import (
    load_image_cv2,
    bgr_to_pil,
    resize_to_fit,
    pil_to_photoimage,
    SUPPORTED_IMAGE_FORMATS,
)

CANVAS_W = 700
CANVAS_H = 480


class ImageTab(ctk.CTkFrame):
    """
    Tab containing image browsing, detection, preview canvas, and save button.
    """

    def __init__(self, parent, detector, status_callback, stats_callback, **kwargs):
        super().__init__(parent, **kwargs)

        self._detector = detector
        self._set_status = status_callback
        self._update_stats = stats_callback

        self._current_file = None
        self._annotated_bgr = None
        self._photo_ref = None  # keep reference to prevent GC

        self._build_ui()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build all widgets for the image tab."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Top toolbar ──────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self._browse_btn = ctk.CTkButton(
            toolbar, text="📂  Browse Image", command=self._browse_image, width=150
        )
        self._browse_btn.pack(side="left", padx=(0, 8))

        self._file_label = ctk.CTkLabel(
            toolbar, text="No file selected", text_color="gray", anchor="w"
        )
        self._file_label.pack(side="left", padx=(0, 20), fill="x", expand=True)

        self._detect_btn = ctk.CTkButton(
            toolbar,
            text="🔍  Detect Animals",
            command=self._run_detection,
            state="disabled",
            width=150,
            fg_color="#2E8B57",
            hover_color="#1F6B3E",
        )
        self._detect_btn.pack(side="left", padx=(0, 8))

        self._save_btn = ctk.CTkButton(
            toolbar,
            text="💾  Save Result",
            command=self._save_image,
            state="disabled",
            width=130,
            fg_color="#1E5A8C",
            hover_color="#154070",
        )
        self._save_btn.pack(side="left", padx=(0, 8))

        # ── Confidence slider ────────────────────────────────────────
        slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        slider_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")

        ctk.CTkLabel(slider_frame, text="Confidence Threshold:").pack(
            side="left", padx=(0, 8)
        )

        self._conf_var = ctk.DoubleVar(value=0.4)
        self._conf_label = ctk.CTkLabel(slider_frame, text="0.40", width=40)
        self._conf_label.pack(side="right", padx=(8, 0))

        self._conf_slider = ctk.CTkSlider(
            slider_frame,
            from_=0.1,
            to=0.9,
            variable=self._conf_var,
            command=self._on_slider_change,
        )
        self._conf_slider.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # ── Canvas ────────────────────────────────────────────────────
        canvas_frame = ctk.CTkFrame(self)
        canvas_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

        self._canvas = tk.Canvas(
            canvas_frame,
            bg="#1a1a2e",
            highlightthickness=0,
            width=CANVAS_W,
            height=CANVAS_H,
        )
        self._canvas.pack(fill="both", expand=True)

        self._canvas_text = self._canvas.create_text(
            CANVAS_W // 2,
            CANVAS_H // 2,
            text="Browse an image to get started",
            fill="#555577",
            font=("Helvetica", 16),
        )

    # ------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------

    def _on_slider_change(self, value):
        self._conf_label.configure(text=f"{float(value):.2f}")

    def _browse_image(self):
        """Open file dialog and load selected image to canvas."""
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=SUPPORTED_IMAGE_FORMATS,
        )
        if not path:
            return

        try:
            bgr = load_image_cv2(path)
        except Exception as exc:
            messagebox.showerror("Image Load Error", str(exc))
            return

        self._current_file = path
        self._annotated_bgr = None

        short_name = os.path.basename(path)
        self._file_label.configure(text=short_name, text_color="white")
        self._detect_btn.configure(state="normal")
        self._save_btn.configure(state="disabled")

        self._display_bgr(bgr)
        self._set_status(f"Loaded: {short_name}")

    def _run_detection(self):
        """Run YOLOv8 inference on the current image."""
        if not self._current_file:
            return

        self._set_status("Running detection…")
        self._detect_btn.configure(state="disabled")

        try:
            bgr = load_image_cv2(self._current_file)
            conf = self._conf_var.get()
            annotated, stats = self._detector.detect(bgr, confidence=conf)
        except Exception as exc:
            messagebox.showerror("Detection Error", str(exc))
            self._set_status("Detection failed.")
            self._detect_btn.configure(state="normal")
            return

        self._annotated_bgr = annotated
        self._display_bgr(annotated)
        self._update_stats(stats)
        self._save_btn.configure(state="normal")
        self._detect_btn.configure(state="normal")

        carnivore_count = stats["carnivores"]
        total = stats["total"]
        self._set_status(
            f"Detection complete — {total} animal(s) found, "
            f"{carnivore_count} carnivore(s)"
        )

        # [FR-12] Popup after image detection
        messagebox.showinfo(
            "Detection Results",
            f"Detection complete!\n\n"
            f"Total animals detected: {total}\n"
            f"Carnivores (red boxes): {carnivore_count}\n"
            f"Non-carnivores (green boxes): {total - carnivore_count}",
        )

    def _save_image(self):
        """Save the annotated image to disk."""
        if self._annotated_bgr is None:
            messagebox.showwarning("Nothing to Save", "Run detection first.")
            return

        try:
            import cv2
        except ImportError:
            messagebox.showerror("Error", "OpenCV not available.")
            return

        base = os.path.splitext(os.path.basename(self._current_file))[0]
        default_name = f"{base}_annotated.jpg"

        save_path = filedialog.asksaveasfilename(
            title="Save Annotated Image",
            initialfile=default_name,
            defaultextension=".jpg",
            filetypes=[
                ("JPEG", "*.jpg"),
                ("PNG", "*.png"),
                ("All Files", "*.*"),
            ],
        )
        if not save_path:
            return

        try:
            cv2.imwrite(save_path, self._annotated_bgr)
            self._set_status(f"Saved: {os.path.basename(save_path)}")
            messagebox.showinfo("Saved", f"Image saved to:\n{save_path}")
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _display_bgr(self, bgr_frame):
        """Convert BGR frame to PIL, resize to canvas, display."""
        pil_img = bgr_to_pil(bgr_frame)

        # Get actual canvas size
        self._canvas.update_idletasks()
        cw = self._canvas.winfo_width() or CANVAS_W
        ch = self._canvas.winfo_height() or CANVAS_H

        pil_img = resize_to_fit(pil_img, cw, ch)
        photo = pil_to_photoimage(pil_img)

        # Keep reference so GC doesn't collect it
        self._photo_ref = photo

        self._canvas.delete("all")
        self._canvas.create_image(cw // 2, ch // 2, anchor="center", image=photo)
