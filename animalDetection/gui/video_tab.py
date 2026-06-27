"""
Video Detection Tab for the Animal Detection & Classification System.
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
    raise ImportError("tkinter not available.")

import threading
import time
import os

from utils.image_utils import bgr_to_pil, resize_to_fit, pil_to_photoimage
from utils.video_utils import (
    open_video_file,
    open_webcam,
    get_video_fps,
    SUPPORTED_VIDEO_FORMATS,
)

CANVAS_W = 700
CANVAS_H = 480


class VideoTab(ctk.CTkFrame):
    """
    Tab for live video detection from file or webcam.
    Video processing runs in a background thread.
    """

    def __init__(self, parent, detector, status_callback, stats_callback, **kwargs):
        super().__init__(parent, **kwargs)

        self._detector = detector
        self._set_status = status_callback
        self._update_stats = stats_callback

        self._video_path = None
        self._use_webcam = False

        self._stop_event = threading.Event()
        self._video_thread = None
        self._photo_ref = None  # prevent GC

        self._build_ui()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build all widgets for the video tab."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Top toolbar ──────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self._browse_btn = ctk.CTkButton(
            toolbar, text="📂  Browse Video", command=self._browse_video, width=150
        )
        self._browse_btn.pack(side="left", padx=(0, 8))

        # Webcam toggle
        self._webcam_var = ctk.BooleanVar(value=False)
        self._webcam_chk = ctk.CTkCheckBox(
            toolbar,
            text="Use Webcam",
            variable=self._webcam_var,
            command=self._toggle_webcam,
        )
        self._webcam_chk.pack(side="left", padx=(0, 20))

        self._file_label = ctk.CTkLabel(
            toolbar, text="No source selected", text_color="gray", anchor="w"
        )
        self._file_label.pack(side="left", padx=(0, 20), fill="x", expand=True)

        self._start_btn = ctk.CTkButton(
            toolbar,
            text="▶  Start",
            command=self._start_video,
            state="disabled",
            width=100,
            fg_color="#2E8B57",
            hover_color="#1F6B3E",
        )
        self._start_btn.pack(side="left", padx=(0, 8))

        self._stop_btn = ctk.CTkButton(
            toolbar,
            text="⏹  Stop",
            command=self._stop_video,
            state="disabled",
            width=100,
            fg_color="#8B2E2E",
            hover_color="#6B1F1F",
        )
        self._stop_btn.pack(side="left", padx=(0, 8))

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

        # ── FPS label ────────────────────────────────────────────────
        self._fps_label = ctk.CTkLabel(
            self, text="FPS: --", text_color="#00BFFF", font=("Courier", 13, "bold")
        )
        self._fps_label.grid(row=1, column=0, padx=(0, 10), pady=(0, 5), sticky="e")

        # ── Canvas ────────────────────────────────────────────────────
        canvas_frame = ctk.CTkFrame(self)
        canvas_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self._canvas = tk.Canvas(
            canvas_frame,
            bg="#1a1a2e",
            highlightthickness=0,
            width=CANVAS_W,
            height=CANVAS_H,
        )
        self._canvas.pack(fill="both", expand=True)

        self._canvas.create_text(
            CANVAS_W // 2,
            CANVAS_H // 2,
            text="Browse a video or enable webcam",
            fill="#555577",
            font=("Helvetica", 16),
        )

    # ------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------

    def _on_slider_change(self, value):
        self._conf_label.configure(text=f"{float(value):.2f}")

    def _toggle_webcam(self):
        """Toggle webcam mode on/off."""
        if self._webcam_var.get():
            self._video_path = None
            self._file_label.configure(text="Webcam (index 0)", text_color="#00BFFF")
            self._start_btn.configure(state="normal")
        else:
            self._file_label.configure(
                text="No source selected"
                if not self._video_path
                else os.path.basename(self._video_path),
                text_color="gray" if not self._video_path else "white",
            )
            if self._video_path:
                self._start_btn.configure(state="normal")
            else:
                self._start_btn.configure(state="disabled")

    def _browse_video(self):
        """Open file dialog and select a video file."""
        path = filedialog.askopenfilename(
            title="Select a Video",
            filetypes=SUPPORTED_VIDEO_FORMATS,
        )
        if not path:
            return

        self._video_path = path
        self._webcam_var.set(False)
        short_name = os.path.basename(path)
        self._file_label.configure(text=short_name, text_color="white")
        self._start_btn.configure(state="normal")
        self._set_status(f"Video selected: {short_name}")

    def _start_video(self):
        """Start the video processing thread."""
        # Reset state for new video
        self._stop_event.clear()
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._browse_btn.configure(state="disabled")

        self._video_thread = threading.Thread(
            target=self._video_loop, daemon=True
        )
        self._video_thread.start()

    def _stop_video(self):
        """Signal the video thread to stop."""
        self._stop_event.set()
        self._stop_btn.configure(state="disabled")
        self._set_status("Stopping video…")

    # ------------------------------------------------------------------
    # VIDEO LOOP (runs in background thread)
    # ------------------------------------------------------------------

    def _video_loop(self):
        """Background thread: read frames, run detection, update canvas."""
        try:
            if self._webcam_var.get():
                cap = open_webcam(0)
            else:
                cap = open_video_file(self._video_path)
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Video Error", str(exc)))
            self.after(0, self._on_video_ended)
            return

        conf = self._conf_var.get()
        carnivore_seen = False
        fps_clock = time.time()
        frame_count = 0

        try:
            while not self._stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break  # end of video or camera disconnected

                # Run detection
                try:
                    annotated, stats = self._detector.detect(frame, confidence=conf)
                except Exception:
                    annotated = frame
                    stats = {"total": 0, "carnivores": 0, "species": {}}

                # [FR-23] Carnivore popup once per video
                if stats["carnivores"] > 0 and not carnivore_seen:
                    carnivore_seen = True
                    count = stats["carnivores"]
                    self.after(
                        0,
                        lambda c=count: messagebox.showwarning(
                            "⚠️ Carnivore Detected!",
                            f"{c} carnivore(s) detected in the video!",
                        ),
                    )

                # FPS calculation
                frame_count += 1
                elapsed = time.time() - fps_clock
                if elapsed >= 0.5:
                    fps = frame_count / elapsed
                    frame_count = 0
                    fps_clock = time.time()
                    self.after(
                        0,
                        lambda f=fps: self._fps_label.configure(
                            text=f"FPS: {f:.1f}"
                        ),
                    )

                # Update canvas in GUI thread
                self.after(0, lambda f=annotated: self._update_canvas(f))

                # Update stats
                self.after(0, lambda s=stats: self._update_stats(s))

                # Small sleep to yield; helps on low-power machines
                time.sleep(0.001)

        finally:
            cap.release()
            self.after(0, self._on_video_ended)

    def _update_canvas(self, bgr_frame):
        """Display a BGR frame on the canvas (called in GUI thread)."""
        pil_img = bgr_to_pil(bgr_frame)

        self._canvas.update_idletasks()
        cw = self._canvas.winfo_width() or CANVAS_W
        ch = self._canvas.winfo_height() or CANVAS_H

        pil_img = resize_to_fit(pil_img, cw, ch)
        photo = pil_to_photoimage(pil_img)

        # Keep reference to prevent GC
        self._photo_ref = photo

        self._canvas.delete("all")
        self._canvas.create_image(cw // 2, ch // 2, anchor="center", image=photo)

    def _on_video_ended(self):
        """Restore button states after video ends/stops."""
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._browse_btn.configure(state="normal")
        self._fps_label.configure(text="FPS: --")
        self._set_status("Video stopped.")
