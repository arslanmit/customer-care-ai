#!/usr/bin/env python3
"""
Script to download and manage spaCy language models for offline installation.
"""
import os
import subprocess
import sys
from pathlib import Path

# Base directory for storing models
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Model URLs with their corresponding package names and versions
MODELS = {
    "en_core_web_md": {
        "url": "https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.7.1/en_core_web_md-3.7.1.tar.gz",
        "filename": "en_core_web_md-3.7.1.tar.gz"
    },
    "es_core_news_md": {
        "url": "https://github.com/explosion/spacy-models/releases/download/es_core_news_md-3.7.0/es_core_news_md-3.7.0.tar.gz",
        "filename": "es_core_news_md-3.7.0.tar.gz"
    },
    "fr_core_news_md": {
        "url": "https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.7.0/fr_core_news_md-3.7.0.tar.gz",
        "filename": "fr_core_news_md-3.7.0.tar.gz"
    },
    "de_core_news_md": {
        "url": "https://github.com/explosion/spacy-models/releases/download/de_core_news_md-3.7.0/de_core_news_md-3.7.0.tar.gz",
        "filename": "de_core_news_md-3.7.0.tar.gz"
    }
}

def download_file(url, filename):
    """Download a file from a URL to the models directory."""
    import urllib.request
    import shutil
    
    filepath = MODELS_DIR / filename
    print(f"Downloading {url}...")
    
    with urllib.request.urlopen(url) as response, open(filepath, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    
    print(f"Saved to {filepath}")
    return filepath

def install_model(filepath):
    """Install a model from a local .tar.gz file."""
    print(f"Installing {filepath}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", str(filepath)])
    print(f"Successfully installed {filepath}")

def main():
    """Download and install all models."""
    print(f"Downloading models to {MODELS_DIR}")
    
    for model_name, model_info in MODELS.items():
        url = model_info["url"]
        filename = model_info["filename"]
        filepath = MODELS_DIR / filename
        
        # Skip if already downloaded
        if filepath.exists():
            print(f"{filename} already exists, skipping download.")
            continue
            
        # Download the model
        try:
            download_file(url, filename)
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            continue
    
    print("\nAll models downloaded. To install them, run:")
    print("pip install -r requirements.txt")
    print("\nOr install a specific model with:")
    print("pip install models/<model-file>.tar.gz")

if __name__ == "__main__":
    main()
