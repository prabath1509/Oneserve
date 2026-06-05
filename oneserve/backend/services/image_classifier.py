from db.models import UserRole
import os
from pathlib import Path

# Global variable to cache YOLO model
_yolo_model = None

def get_yolo_model():
    """
    Load YOLO model (cached for performance)
    Uses YOLOv8 nano for lightweight inference
    """
    global _yolo_model
    
    if _yolo_model is None:
        try:
            import torch
            
            # Monkey-patch torch.load to use weights_only=False for PyTorch 2.6+
            original_load = torch.load
            def patched_load(*args, **kwargs):
                kwargs.setdefault('weights_only', False)
                return original_load(*args, **kwargs)
            torch.load = patched_load
            
            from ultralytics import YOLO
            
            # Model path relative to the root directory
            model_path = Path(__file__).parent.parent.parent.parent / "yolov8n.pt"
            
            if not model_path.exists():
                print(f"⚠ Warning: Model file not found at {model_path}")
                _yolo_model = False
                return None
            
            _yolo_model = YOLO(str(model_path))
            
            # Restore original torch.load
            torch.load = original_load
            
            print("✓ YOLO model loaded successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not load YOLO model: {e}")
            print("  Image detection will be skipped")
            _yolo_model = False
    
    return _yolo_model if _yolo_model is not False else None


def predict_category(image_path: str) -> str:
    """
    Uses YOLOv8 model to predict the complaint category from an image.
    
    Args:
        image_path: Path to the uploaded complaint image
        
    Returns:
        One of: WATER, ELECTRICITY, ROAD, SANITATION, GENERAL
    """
    
    try:
        model = get_yolo_model()
        
        if model is None:
            print("YOLO model not available, falling back to GENERAL")
            return "GENERAL"
        
        # Run inference
        results = model(image_path, verbose=False)
        
        # Get detected objects
        detected_classes = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id].lower()
                    confidence = float(box.conf[0])
                    
                    # Only consider detections with confidence > 0.3
                    if confidence > 0.3:
                        detected_classes.append(class_name)
        
        # Map detected objects to complaint categories
        category = map_objects_to_category(detected_classes)
        return category
        
    except Exception as e:
        print(f"Image classification error: {e}")
        return "GENERAL"


def map_objects_to_category(detected_objects: list) -> str:
    """
    Map detected objects from YOLO to complaint categories.
    
    Args:
        detected_objects: List of detected object class names
        
    Returns:
        Complaint category: WATER, ELECTRICITY, ROAD, SANITATION, or GENERAL
    """
    
    if not detected_objects:
        return "GENERAL"
    
    # Define object-to-category mappings
    water_objects = [
        'fire hydrant', 'sink', 'toilet', 'bottle', 'cup',
        'water', 'faucet', 'tap', 'pipe', 'hydrant'
    ]
    
    electricity_objects = [
        'traffic light', 'tv', 'laptop', 'cell phone', 'microwave',
        'oven', 'toaster', 'refrigerator', 'light', 'monitor',
        'keyboard', 'remote', 'mouse', 'wire', 'cable', 'pole'
    ]
    
    road_objects = [
        'car', 'motorcycle', 'bus', 'truck', 'bicycle',
        'traffic light', 'stop sign', 'parking meter', 'road',
        'street', 'pothole', 'vehicle', 'bridge'
    ]
    
    sanitation_objects = [
        'person', 'backpack', 'umbrella', 'handbag', 'suitcase',
        'bottle', 'bowl', 'banana', 'apple', 'sandwich',
        'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'trash', 'garbage', 'waste', 'bin'
    ]
    
    # Count matches for each category
    category_scores = {
        'WATER': sum(1 for obj in detected_objects if obj in water_objects),
        'ELECTRICITY': sum(1 for obj in detected_objects if obj in electricity_objects),
        'ROAD': sum(1 for obj in detected_objects if obj in road_objects),
        'SANITATION': sum(1 for obj in detected_objects if obj in sanitation_objects),
    }
    
    # Get category with highest score
    max_score = max(category_scores.values())
    
    if max_score == 0:
        return "GENERAL"
    
    # Return category with highest score
    for category, score in category_scores.items():
        if score == max_score:
            return category
    
    return "GENERAL"


def get_officer_role_for_category(category: str) -> UserRole:
    """
    Map complaint category to officer role
    """
    category_to_role = {
        "WATER": UserRole.OFFICER_WATER,
        "ELECTRICITY": UserRole.OFFICER_ELECTRICITY,
        "ROAD": UserRole.OFFICER_ROAD,
        "SANITATION": UserRole.OFFICER_SANITATION,
    }
    return category_to_role.get(category, None)
