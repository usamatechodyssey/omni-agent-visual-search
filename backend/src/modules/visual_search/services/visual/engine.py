import threading
import torch
from PIL import Image
from io import BytesIO
import numpy as np

# CLIP model load karne ke liye library
from transformers import CLIPProcessor, CLIPModel

# Global variables (Singleton pattern - Model sirf ek baar load hoga)
_clip_model_instance = None
_clip_processor_instance = None
_model_lock = threading.Lock()  # Thread-safe lock add kiya


def get_visual_model():
    """
    Thread-safe Singleton Pattern: CLIP model ko sirf tab load karega jab pehli baar zaroorat hogi.
    Parallel requests ke dauran race condition se bachne ke liye lock use karta hai.
    """
    global _clip_model_instance, _clip_processor_instance
    
    if _clip_model_instance is None:
        with _model_lock:  # Double-checked locking
            if _clip_model_instance is None:
                print("👁️ [Visual Engine] Loading CLIP Model (ViT-B/32)...")
                _clip_model_instance = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                _clip_processor_instance = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                _clip_model_instance.eval()
                print("✅ [Visual Engine] CLIP Model Loaded Successfully.")
        
    return _clip_model_instance, _clip_processor_instance


def get_image_embedding(image_bytes: bytes) -> list:
    """
    Image ke bytes leta hai -> CLIP model se guzarta hai -> 512 numbers ki list return karta hai.
    """
    model, processor = get_visual_model()
    
    try:
        # 1. Convert Bytes to Image
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        
        # 2. Process image (Resize, Normalize, Tensor conversion)
        inputs = processor(images=img, return_tensors="pt")
        
        # 3. Generate Embedding
        with torch.no_grad():
            image_features = model.get_image_features(pixel_values=inputs["pixel_values"])
        
        # 4. Flatten & Normalize (L2 normalization for cosine similarity)
        embedding_np = image_features.numpy().flatten()
        norm = np.linalg.norm(embedding_np)
        
        # Zero division se bachne ke liye
        if norm == 0:
            return embedding_np.tolist()
            
        normalized_embedding = (embedding_np / norm).astype('float32')
        
        return normalized_embedding.tolist()
        
    except Exception as e:
        print(f"❌ [Visual Engine] Error processing image: {e}")
        return None