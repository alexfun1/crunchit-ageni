import torch
import gradio as gr
import signal
import gc
import requests
import json
import sys
import base64
from diffusers import StableDiffusionXLPipeline
from transformers import CLIPTokenizer
from PIL import Image
from pathlib import Path
from io import BytesIO

# Configuration
AUTOMATIC1111_URL = "http://127.0.0.1:7860"  # Change if needed

# Load CLIP tokenizer for truncation
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")

# Folder for storing generated images
gallery_folder = Path("generated_images")
gallery_folder.mkdir(exist_ok=True)

# List to store image paths
image_gallery = list(gallery_folder.glob("*.png"))

def truncate_prompt(prompt, max_length=77):
    """Truncate the prompt to 77 tokens to prevent CLIP errors"""
    tokenized = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_length)
    return tokenizer.decode(tokenized["input_ids"][0], skip_special_tokens=True)

def generate_locally(prompt, negative_prompt):
    """Dynamically load model, generate image, and unload to free VRAM"""
    model_id = "Fluently/Fluently-XL-Final"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("[INFO] Loading Fluently-XL-Final model...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    pipe.to(device)
    pipe.enable_attention_slicing()
    pipe.enable_model_cpu_offload()

    # Truncate prompts
    prompt = truncate_prompt(prompt if prompt else "")
    negative_prompt = truncate_prompt(negative_prompt if negative_prompt else "")

    # Generate image
    print("[INFO] Generating image locally...")
    image = pipe(prompt=prompt, negative_prompt=negative_prompt, width=768, height=768).images[0]

    # Save the image
    img_path = gallery_folder / f"generated_{len(image_gallery) + 1}.png"
    image.save(img_path)

    # Add to gallery
    image_gallery.append(img_path)

    # Cleanup VRAM
    print("[INFO] Unloading Fluently-XL-Final model to free VRAM...")
    del pipe
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    return image, [str(img) for img in image_gallery]

def generate_with_automatic1111(prompt, negative_prompt):
    """Submit request to Automatic1111 API"""
    try:
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": 768,
            "height": 768,
            "steps": 20,
            "cfg_scale": 7,
            "sampler_index": "Euler a"
        }

        response = requests.post(f"{AUTOMATIC1111_URL}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()

        # Convert base64 response to image
        result = response.json()
        if "images" in result:
            image_data = result["images"][0]
            image = Image.open(BytesIO(base64.b64decode(image_data)))

            # Save image
            img_path = gallery_folder / f"generated_{len(image_gallery) + 1}.png"
            image.save(img_path)

            # Add to gallery
            image_gallery.append(img_path)

            return image, [str(img) for img in image_gallery]
        else:
            return None, image_gallery
    except Exception as e:
        return f"Error: {str(e)}", image_gallery

def generate_image(prompt, negative_prompt, platform):
    """Decide whether to use local model or Automatic1111"""
    if platform == "Local (Fluently-XL-Final)":
        return generate_locally(prompt, negative_prompt)
    elif platform == "Automatic1111":
        return generate_with_automatic1111(prompt, negative_prompt)
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

# Register the cleanup handler
signal.signal(signal.SIGINT, cleanup_handler)

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Fluently-XL-Final & Automatic1111 Image Generator")

    with gr.Row():
        prompt_input = gr.Textbox(label="Prompt", placeholder="Enter your prompt here...")
        neg_prompt_input = gr.Textbox(label="Negative Prompt", placeholder="Enter negative prompt here...")

    platform_selector = gr.Radio(
        ["Local (Fluently-XL-Final)", "Automatic1111"],
        label="Select Generation Platform",
        value="Local (Fluently-XL-Final)"
    )

    generate_button = gr.Button("Generate Image")

    with gr.Row():
        output_image = gr.Image(label="Generated Image", interactive=False)

    gr.Markdown("### Image Gallery")
    image_gallery_ui = gr.Gallery(label="Generated Images", interactive=False, columns=4, height=300)

    generate_button.click(generate_image, inputs=[prompt_input, neg_prompt_input, platform_selector], outputs=[output_image, image_gallery_ui])

# Run the app with cleanup on exit
try:
    demo.launch()
except KeyboardInterrupt:
    cleanup()
    sys.exit(0)
