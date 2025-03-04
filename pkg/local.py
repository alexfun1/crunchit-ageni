from  transformers import CLIPTokenizer
import gc
import torch
from diffusers import StableDiffusionXLPipeline
from pkg.loras import apply_loras
from pkg.globals import *

tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")

def truncate_prompt(prompt, max_length=77):
    """Truncate the prompt to 77 tokens to prevent CLIP errors"""
    tokenized = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_length)
    return tokenizer.decode(tokenized["input_ids"][0], skip_special_tokens=True)

def generate_locally(prompt, selected_loras, use_reactor, use_adetailer, gallery_folder, image_gallery):
    """Dynamically load model, apply LoRAs, and generate image"""
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

    # Apply LoRAs (if selected)
    if selected_loras:
        prompt = apply_loras(LORA_CONFIG, prompt, selected_loras)
        print(f"[INFO] Resulting prompt after applying LoRAs: {prompt}")

    # Apply ReActor
    if use_reactor:
        print("[INFO] ReActor is enabled")
        prompt = f"{prompt}, (reactor:1.2)"

    # Apply ADetailer
    if use_adetailer:
        print("[INFO] ADetailer is enabled")
        prompt = f"{prompt}, (adetailer:1.2)"

    # Generate image
    print("[INFO] Generating image locally...")
    image = pipe(prompt=truncate_prompt(prompt), negative_prompt=truncate_prompt(NEG_PROMPT), width=768, height=768).images[0]

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