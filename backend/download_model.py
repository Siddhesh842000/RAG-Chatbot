"""
Downloads the embedding model so it is stored with the app.

Used as part of the Render build step:
    pip install -r requirements.txt && python download_model.py

It only downloads files (it does not load PyTorch), so it uses very little memory.
If MODEL_CACHE_DIR is not set, the model goes to the normal Hugging Face cache.

The model repository also contains copies for TensorFlow, ONNX and others (about
840 MB in total). We only download the files that sentence-transformers needs
(about 90 MB). If a file is ever missing, sentence-transformers fetches it by itself.
"""
from huggingface_hub import snapshot_download

from app.config import settings

NEEDED_FILES = [
    "README.md",
    "modules.json",
    "config_sentence_transformers.json",
    "sentence_bert_config.json",
    "config.json",
    "model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "vocab.txt",
    "1_Pooling/config.json",
]

path = snapshot_download(
    repo_id=settings.EMBEDDING_MODEL,
    cache_dir=settings.MODEL_CACHE_DIR,
    allow_patterns=NEEDED_FILES,
)
print(f"Model files are ready in: {path}")
