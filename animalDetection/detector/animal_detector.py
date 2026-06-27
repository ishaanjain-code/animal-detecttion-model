"""
Animal detector module using YOLOv8 for detection and classification.
"""

try:
    import cv2
except ImportError:
    raise ImportError(
        "OpenCV not found. Install with: pip install opencv-python-headless"
    )

try:
    from ultralytics import YOLO
except ImportError:
    raise ImportError(
        "Ultralytics not found. Install with: pip install ultralytics"
    )

import numpy as np
from detector.carnivore_list import CARNIVORES, ALL_ANIMALS

# Bounding box colors (BGR format for OpenCV)
COLOR_CARNIVORE = (0, 0, 255)    # RED
COLOR_OTHER = (0, 255, 0)        # GREEN


class AnimalDetector:
    """
    Handles loading the YOLOv8 model and running animal detection inference.
    """

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the YOLOv8n model (auto-downloads if not present)."""
        try:
            self.model = YOLO("yolov8n.pt")
        except Exception as e:
            raise RuntimeError(
                f"Failed to load YOLOv8 model: {e}\n"
                "Ensure you have an internet connection for first-time download."
            )

    def detect(self, frame: np.ndarray, confidence: float = 0.4):
        """
        Run detection on a frame and return annotated frame + stats.

        Args:
            frame: BGR image as numpy array
            confidence: confidence threshold (0.1 to 0.9)

        Returns:
            annotated_frame: BGR image with bounding boxes drawn
            stats: dict with 'total', 'carnivores', 'species'
        """
        if self.model is None:
            raise RuntimeError("Model not loaded.")

        results = self.model.predict(source=frame, conf=confidence, verbose=False)

        annotated = frame.copy()
        total_animals = 0
        carnivore_count = 0
        species_counts = {}

        for result in results:
            if result.boxes is None:
                continue

            boxes_xyxy = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            confs = result.boxes.conf.cpu().numpy()

            for (x1, y1, x2, y2), cls_id, conf in zip(boxes_xyxy, classes, confs):
                class_name = self.model.names.get(cls_id, "")

                # Only process COCO animal classes
                if class_name not in ALL_ANIMALS:
                    continue

                total_animals += 1
                is_carnivore = class_name in CARNIVORES

                if is_carnivore:
                    carnivore_count += 1
                    color = COLOR_CARNIVORE
                else:
                    color = COLOR_OTHER

                # Track species
                species_counts[class_name] = species_counts.get(class_name, 0) + 1

                # Draw bounding box
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

                # Draw label: species + confidence
                label = f"{class_name} {conf * 100:.1f}%"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                thickness = 2
                (text_w, text_h), baseline = cv2.getTextSize(
                    label, font, font_scale, thickness
                )

                # Background rectangle for label
                label_y = max(y1 - 5, text_h + 5)
                cv2.rectangle(
                    annotated,
                    (x1, label_y - text_h - baseline),
                    (x1 + text_w, label_y + baseline),
                    color,
                    cv2.FILLED,
                )
                cv2.putText(
                    annotated, label,
                    (x1, label_y - baseline),
                    font, font_scale, (255, 255, 255), thickness
                )

        stats = {
            "total": total_animals,
            "carnivores": carnivore_count,
            "species": species_counts,
        }
        return annotated, stats
