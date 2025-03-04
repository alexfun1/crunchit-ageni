import os
import base64
from io import BytesIO
from PIL import Image
import gradio as gr

# Define folder locations
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

def create_thumbnail(image_path, scale=0.1):
    """
    Create a thumbnail at the specified scale and save it if it doesn't exist.
    Returns the path to the saved thumbnail.
    """
    filename = os.path.basename(image_path)
    thumbnail_path = os.path.join(THUMBNAIL_DIR, f"thumb_{filename}")

    # Skip creation if thumbnail already exists
    if not os.path.exists(thumbnail_path):
        with Image.open(image_path) as img:
            new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))  # Prevent zero size
            img.thumbnail(new_size)
            img.save(thumbnail_path, format="PNG")

    return thumbnail_path

def encode_image(image_path):
    """
    Encode the original full-size image as base64.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def get_gallery():
    """
    Generates a gallery where only thumbnails (icons) are displayed.
    Clicking on an image returns the base64 of the original full-size image.
    """
    image_paths = get_depth_images()
    gallery_data = []

    for img_path in image_paths:
        thumbnail_path = create_thumbnail(img_path)  # Generate & store thumbnail if not exists
        gallery_data.append((thumbnail_path, img_path))  # (Thumbnail, Full Image Path)

    return gallery_data

def on_image_click(selection):
    """
    Callback function: Returns the base64-encoded original full-size image when clicked.
    """
    print(selection)
    if isinstance(selection, tuple) and len(selection) == 2:
        _, image_path = selection  # Extract the full image path from the tuple
        return encode_image(image_path)
    return "Error: No image selected"

# Get images initially so that they load immediately
initial_gallery_data = get_gallery()

# Gradio UI
with gr.Blocks() as depth_gallery_ui:
    gr.Markdown("# 📂 Depth Image Gallery - Icons Only")

    refresh_button = gr.Button("Reload Images")

    gallery = gr.Gallery(label="Depth Image Icons", interactive=True, value=initial_gallery_data)
    selected_image_output = gr.Textbox(label="Base64 Encoded Original Image", interactive=False, lines=4)

    # Reload images when button is clicked
    refresh_button.click(get_gallery, outputs=[gallery])

    # Click an icon to get the original image in base64
    gallery.select(on_image_click, inputs=[gallery], outputs=[selected_image_output])

if __name__ == "__main__":
    depth_gallery_ui.launch()
