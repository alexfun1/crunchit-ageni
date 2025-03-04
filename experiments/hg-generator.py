import torch
import gradio as gr
import signal
import gc
from diffusers import StableDiffusionXLPipeline, StableDiffusionPipeline
from transformers import CLIPTokenizer
from PIL import Image
from pathlib import Path
import sys

# Load the correct SDXL pipeline
model_id = "Kernel/sd-nsfw"
device = "cuda" if torch.cuda.is_available() else "cpu"

pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda") if device == "cuda" else pipe.to("cpu")
pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))

# Apply memory optimizations
pipe.to(device)
pipe.enable_attention_slicing()
pipe.enable_model_cpu_offload()

# Load CLIP tokenizer (to count tokens)
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

def generate_image(prompt, negative_prompt):
    # Ensure prompts are not None
    prompt = truncate_prompt(prompt if prompt else "")
    negative_prompt = truncate_prompt(negative_prompt if negative_prompt else "")

    # Generate image with smaller resolution to save memory
    image = pipe(prompt=prompt, negative_prompt=negative_prompt, width=768, height=768).images[0]
    
    # Save the image
    img_path = gallery_folder / f"generated_{len(image_gallery) + 1}.png"
    image.save(img_path)
    
    # Add to gallery
    image_gallery.append(img_path)
    
    return image, [str(img) for img in image_gallery]

# Cleanup function to release GPU memory
def cleanup():
    print("\n[INFO] Cleaning up before exit...")
    global pipe
    if "pipe" in globals():
        del pipe
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    print("[INFO] VRAM released successfully!")

# Handle Ctrl+C (SIGINT)
def cleanup_handler(signum, frame):
    cleanup()
    sys.exit(0)  # Exit safely

# Register the cleanup handler
signal.signal(signal.SIGINT, cleanup_handler)

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Fluently-XL-Final Image Generator (Optimized for Low VRAM)")
    
    with gr.Row():
        prompt_input = gr.Textbox(label="Prompt", placeholder="Enter your prompt here...")
        neg_prompt_input = gr.Textbox(label="Negative Prompt", placeholder="Enter negative prompt here...")
    
    generate_button = gr.Button("Generate Image")
    
    with gr.Row():
        output_image = gr.Image(label="Generated Image", interactive=False)
    
    gr.Markdown("### Image Gallery")
    image_gallery_ui = gr.Gallery(label="Generated Images", interactive=False, columns=4, height=300)
    
    generate_button.click(generate_image, inputs=[prompt_input, neg_prompt_input], outputs=[output_image, image_gallery_ui])

# Run the app with cleanup on exit
try:
    demo.launch()
except KeyboardInterrupt:
    cleanup()
    sys.exit(0)
