# 🦁 Animal Detection & Classification System

A desktop application that uses **YOLOv8** to detect and classify animals in
images and live video, highlighting carnivores in **red** and non-carnivores in **green**.

---

## ✨ Features

- 🖼️ **Image Detection** — browse any JPG/PNG/BMP/WebP image and run instant inference
- 🎬 **Video Detection** — process MP4/AVI/MOV/MKV files or a live webcam stream
- 🔴🟢 **Colour-coded bounding boxes** — red for carnivores, green for others
- 📊 **Stats panel** — live counts of total animals, carnivores, and species breakdown
- ⚡ **FPS counter** during video processing
- 💾 **Save annotated images** with one click
- 🎚️ **Adjustable confidence threshold** (0.10 – 0.90)
- ⚠️ **Carnivore popup alerts** — on image detection and once per video

### Supported Animals (COCO classes)
`bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe`

### Carnivore Classification
`cat`, `dog`, `bear` → **RED** boxes  
All others → **GREEN** boxes

---

## 🛠️ Installation

### Prerequisites
- Python 3.10 or later
- pip
- Internet connection (for first-time YOLOv8 model download ~6 MB)

### Steps

```bash
# 1. Clone or download the project
git clone <repo-url>
cd animal_detection

# 2. (Recommended) Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the Application

```bash
python main.py
```

The first run will automatically download the `yolov8n.pt` weights file (~6 MB).

---

## 📁 Project Structure

```
animal_detection/
├── main.py                   # Entry point
├── requirements.txt          # Pinned dependencies
├── README.md                 # This file
│
├── gui/
│   ├── __init__.py
│   ├── app.py                # Root window, header, stats panel, status bar
│   ├── image_tab.py          # Image Detection tab
│   └── video_tab.py          # Video Detection tab
│
├── detector/
│   ├── __init__.py
│   ├── animal_detector.py    # YOLOv8 inference + annotation
│   └── carnivore_list.py     # Animal & carnivore lists
│
└── utils/
    ├── __init__.py
    ├── image_utils.py        # Image loading, conversion, resize helpers
    └── video_utils.py        # VideoCapture helpers
```

---

## 🎛️ Usage Guide

### Image Detection Tab
1. Click **Browse Image** and select a file (JPG, JPEG, PNG, BMP, WEBP).
2. Adjust the **Confidence Threshold** slider if needed.
3. Click **Detect Animals** — the annotated image replaces the preview.
4. A popup shows total animals and carnivore count.
5. Click **Save Result** to export the annotated image.

### Video Detection Tab
1. Click **Browse Video** and select a file (MP4, AVI, MOV, MKV),  
   **or** tick **Use Webcam** to use your default camera.
2. Adjust the confidence slider.
3. Click **▶ Start** — annotated frames appear live with an FPS counter.
4. Click **⏹ Stop** to halt processing cleanly at any time.
5. A carnivore warning popup appears the **first** time a carnivore is detected.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `ImportError: customtkinter` | `pip install customtkinter` |
| `ImportError: ultralytics` | `pip install ultralytics` |
| Model download fails | Check internet connection; try again |
| Webcam not opening | Ensure camera is connected and not used by another app |
| Low FPS on video | Lower the confidence threshold; use a GPU-enabled PyTorch build |

---

## 📄 License

MIT License — free to use and modify.
