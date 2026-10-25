"""
Downloads the embedding model so it is stored with the app.

Used as part of the Render build step:
    pip install -r requirements.txt && python download_model.py

The model is all-MiniLM-L6-v2 in ONNX format (about 90 MB), loaded with fastembed.
If MODEL_CACHE_DIR is not set, the model goes to fastembed's default cache folder.
"""
from app.config import settings
from app.services.embedding_service import get_model

get_model()  # downloads the model (if needed) and loads it once to prove it works
print(f"Model is ready: {settings.EMBEDDING_MODEL}")
print(f"Stored in: {settings.MODEL_CACHE_DIR or 'the default cache folder'}")
