# animal-detecttion-model
# 🦁 Animal Detection & Classification System

A Python desktop app that detects and classifies animals in images and videos using **YOLOv8**. Carnivores are highlighted in **red**, others in **green**.

---

## 📸 Features

- Detect animals in images and live video
- 🔴 Red boxes for carnivores (cat, dog, bear)
- 🟢 Green boxes for non-carnivores (bird, horse, cow, etc.)
- Live webcam support
- Confidence threshold slider
- Save annotated images
- Real-time FPS counter
- Species stats panel

---

## 🛠️ Tech Stack

- **YOLOv8** (Ultralytics) — object detection
- **customtkinter** — modern GUI
- **OpenCV** — image & video processing
- **Pillow** — image rendering in GUI

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/animal-detection.git
cd animal-detection
```

### 2. Install dependencies
```bash
pip install ultralytics opencv-python customtkinter Pillow
```

### 3. Run the app
```bash
python main.py
```
> The YOLOv8 model (~6 MB) will auto-download on first run.

---

## 📁 Project Structure

```
animalDetection/
├── main.py
├── detector/
│   ├── animal_detector.py
│   └── carnivore_list.py
├── gui/
│   ├── app.py
│   ├── image_tab.py
│   └── video_tab.py
└── utils/
    ├── image_utils.py
    └── video_utils.py
```

---

## ⚠️ Requirements

- Python 3.10, 3.11, or 3.12 (3.14 not supported by PyTorch yet)
- Internet connection for first-time model download

---

## 📄 License

MIT License — free to use and modify.
