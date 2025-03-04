# Description: Helper functions for the main application.
from transformers import CLIPTokenizer
from pathlib import Path
from pkg.loras import *
import  pkg.globals as globals
import pkg.resolutions as resolutions
from pkg.automatic import *
from pkg.local import *
import base64
import os
import numpy as np
from PIL import Image
from io import BytesIO
import signal
import gc
import sys

#Poses depth maps
DEPTH_DIR = "./depth_images"
THUMBNAIL_DIR = f"{DEPTH_DIR}/temp_thumbnails"
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def get_depth_images():
    """
    Scan the DEPTH_DIR (including subfolders) for images containing '_depth' in their filenames.
    Return a list of image paths.
    """
    depth_images = []
    
    for root, _, files in os.walk(DEPTH_DIR):
        for file in files:
            if "_depth" in file.lower() and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                depth_images.append(os.path.join(root, file))

    return depth_images

def encode_image(image_path):
    """
    Encode the original full-size image as base64.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
def convert_image_to_base64(image):
    """
    Convert uploaded image (NumPy array from gr.Image) to Base64.
    """
    if image is None:
        return ""  # Return empty string if no image uploaded
    
    # Convert NumPy array to PIL Image
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    # Convert PIL image to Base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # Save as PNG format
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64  # Return Base64 string

# Folder for storing generated images
gallery_folder = Path("generated_images")
gallery_folder.mkdir(exist_ok=True)

# List to store image paths
image_gallery = list(gallery_folder.glob("*.png"))

def generate_image(prompt, platform,  selected_loras, resolution_selector, use_reactor, use_adetailer, model_name, pose_base64, use_pose, reactor_img_base64, reactor_method, reactor_models):
    """Decide whether to use local model or Automatic1111"""
    selected_lora_ids = [desc for desc in selected_loras if desc in LORA_CONFIG]
    print(f"Selected Resolutions: {resolution_selector}")
    if platform == "Local (Fluently-XL-Final)":
        return generate_locally(prompt, selected_lora_ids, use_reactor, use_adetailer, gallery_folder, image_gallery)
    elif platform == "Automatic1111":
        print ("automatic1111")
        if not reactor_img_base64.strip():  # Check if the string is empty or contains only whitespace
           reactor_img_base64=encode_image("/home/fun/Projects/crunchit-ageni/face_images/pexels-olly-3812743-1.jpg")
           print("Default image used")
        if reactor_method == "Image":
            ops_22 = 0
        elif reactor_method == "Model":
            ops_22 = 1
        return generate_with_automatic1111(prompt, selected_lora_ids, resolution_selector, use_reactor, use_adetailer, gallery_folder, image_gallery, model_name, pose_base64, use_pose, reactor_img_base64, ops_22, reactor_models)
    else:
        return "Invalid Platform Selection", image_gallery

# Cleanup function to release GPU memory
def cleanup():
    print("\n[INFO] Cleaning up before exit...")
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    print("[INFO] VRAM released successfully!")

# Handle Ctrl+C (SIGINT)
def cleanup_handler(signum, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_handler)

#prompt editor functions

# Load prompt structure from external JSON file
# Load prompt structure from external JSON file
def load_prompt_structure():
    with open("prompt_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Save updated prompt structure to JSON file
def save_prompt_structure(data):
    with open("prompt_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Load data from JSON
PROMPT_DATA = load_prompt_structure()

# Function to generate SD prompt string based on selected values
def build_prompt(main_items, descriptions, positions):
    """Creates an ordered prompt string from selected dropdown values."""
    
    if not isinstance(main_items, list):
        main_items = [main_items] if main_items else []
    
    if not isinstance(descriptions, list):
        descriptions = [descriptions] if descriptions else []
    
    if not isinstance(positions, list):
        positions = [positions] if positions else []

    ordered_prompt = []
    
    # Add main items
    if main_items:
        ordered_prompt.append(", ".join(main_items))

    # Add additional descriptions if any
    if descriptions:
        ordered_prompt.append(", ".join(descriptions))

    # Add positioning if any
    if positions:
        ordered_prompt.append(", ".join(positions))

    return " | ".join(ordered_prompt) if ordered_prompt else "No prompt selected."
