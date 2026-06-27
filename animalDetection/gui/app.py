"""
Main application window for the Animal Detection & Classification System.
"""

try:
    import customtkinter as ctk
except ImportError:
    raise ImportError(
        "customtkinter not found. Install with: pip install customtkinter"
    )

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    raise ImportError("tkinter not available — ensure you have a full Python install.")

from gui.image_tab import ImageTab
from gui.video_tab import VideoTab


class AnimalDetectionApp(ctk.CTk):
    """
    Root application window containing the header, tab view, stats panel,
    and status bar.
    """

    def __init__(self, detector):
        super().__init__()

        self._detector = detector

        self.title("Animal Detection & Classification System")
        self.geometry("1100x750")
        self.minsize(900, 620)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._build_ui()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build the full application layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # ── [FR-06] Header ────────────────────────────────────────────
        header = ctk.CTkFrame(self, height=60, fg_color="#0d0d2b")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="🦁  Animal Detection & Classification System",
            font=("Helvetica", 22, "bold"),
            text_color="#00BFFF",
        ).pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            header,
            text="Powered by YOLOv8",
            font=("Helvetica", 11),
            text_color="#5588AA",
        ).pack(side="right", padx=20)

        # ── [FR-02] Tab view ──────────────────────────────────────────
        self._tab_view = ctk.CTkTabview(self, anchor="nw")
        self._tab_view.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")

        self._tab_view.add("🖼  Image Detection")
        self._tab_view.add("🎬  Video Detection")

        # ── [FR-07] Stats panel ───────────────────────────────────────
        stats_panel = ctk.CTkFrame(self, width=220)
        stats_panel.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="ns")
        stats_panel.grid_propagate(False)

        ctk.CTkLabel(
            stats_panel,
            text="📊  Detection Stats",
            font=("Helvetica", 15, "bold"),
            text_color="#00BFFF",
        ).pack(pady=(15, 10), padx=10)

        ctk.CTkFrame(stats_panel, height=1, fg_color="#333355").pack(
            fill="x", padx=10
        )

        self._stat_total_label = ctk.CTkLabel(
            stats_panel, text="Total Animals: 0", anchor="w"
        )
        self._stat_total_label.pack(fill="x", padx=15, pady=(12, 4))

        self._stat_carnivore_label = ctk.CTkLabel(
            stats_panel,
            text="Carnivores 🔴: 0",
            anchor="w",
            text_color="#FF6666",
        )
        self._stat_carnivore_label.pack(fill="x", padx=15, pady=4)

        self._stat_other_label = ctk.CTkLabel(
            stats_panel,
            text="Non-carnivores 🟢: 0",
            anchor="w",
            text_color="#66FF99",
        )
        self._stat_other_label.pack(fill="x", padx=15, pady=4)

        ctk.CTkFrame(stats_panel, height=1, fg_color="#333355").pack(
            fill="x", padx=10, pady=(10, 4)
        )

        ctk.CTkLabel(
            stats_panel,
            text="Species Detected:",
            font=("Helvetica", 12, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(6, 4))

        # Scrollable species list
        self._species_frame = ctk.CTkScrollableFrame(
            stats_panel, fg_color="transparent", height=250
        )
        self._species_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._species_labels = {}

        # ── [FR-05] Status bar ────────────────────────────────────────
        self._status_bar = ctk.CTkLabel(
            self,
            text="Ready — load an image or video to begin.",
            anchor="w",
            fg_color="#0a0a1e",
            text_color="#AAAACC",
            corner_radius=0,
            height=28,
        )
        self._status_bar.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0
        )

        # ── Instantiate tabs ──────────────────────────────────────────
        tab_image = self._tab_view.tab("🖼  Image Detection")
        tab_image.grid_columnconfigure(0, weight=1)
        tab_image.grid_rowconfigure(0, weight=1)

        self._image_tab = ImageTab(
            tab_image,
            detector=self._detector,
            status_callback=self._set_status,
            stats_callback=self._update_stats,
        )
        self._image_tab.grid(row=0, column=0, sticky="nsew")

        tab_video = self._tab_view.tab("🎬  Video Detection")
        tab_video.grid_columnconfigure(0, weight=1)
        tab_video.grid_rowconfigure(0, weight=1)

        self._video_tab = VideoTab(
            tab_video,
            detector=self._detector,
            status_callback=self._set_status,
            stats_callback=self._update_stats,
        )
        self._video_tab.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # CALLBACKS
    # ------------------------------------------------------------------

    def _set_status(self, text: str):
        """Update the status bar text."""
        self._status_bar.configure(text=f"  {text}")

    def _update_stats(self, stats: dict):
        """Refresh the stats panel with new detection data."""
        total = stats.get("total", 0)
        carnivores = stats.get("carnivores", 0)
        others = total - carnivores
        species = stats.get("species", {})

        self._stat_total_label.configure(text=f"Total Animals: {total}")
        self._stat_carnivore_label.configure(text=f"Carnivores 🔴: {carnivores}")
        self._stat_other_label.configure(text=f"Non-carnivores 🟢: {others}")

        # Clear old species labels
        for widget in self._species_frame.winfo_children():
            widget.destroy()
        self._species_labels.clear()

        if not species:
            ctk.CTkLabel(
                self._species_frame,
                text="(none detected)",
                text_color="gray",
                anchor="w",
            ).pack(fill="x")
            return

        for name, count in sorted(species.items()):
            from detector.carnivore_list import CARNIVORES
            color = "#FF6666" if name in CARNIVORES else "#66FF99"
            lbl = ctk.CTkLabel(
                self._species_frame,
                text=f"  • {name.capitalize()}: {count}",
                text_color=color,
                anchor="w",
            )
            lbl.pack(fill="x", pady=1)
            self._species_labels[name] = lbl
