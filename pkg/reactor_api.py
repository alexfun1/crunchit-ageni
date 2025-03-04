import requests
import base64
import json
from io import BytesIO
from PIL import Image

# Set AUTOMATIC1111 API URL
reactor_API_URL = "http://127.0.0.1:7860"  # Change if necessary

def reactor_encode_image(image_path):
    """Encode an image as base64 for API requests."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def reactor_generate_facemodel(reactor_reference_image_path):
    """
    Generate a face model from a reference image using the ReActor API.
    """
    payload = {
        "face_image": reactor_encode_image(reactor_reference_image_path),
        "model_name": "custom_face",  # Change this if needed
    }

    response = requests.post(f"{reactor_API_URL}/sdapi/v1/reactor/generate", json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("model_id")  # Return generated model ID
    else:
        print(f"Error: {response.text}")
        return None

def reactor_replace_face(reactor_input_image_path, reactor_model_id):
    """
    Replace the face in an image using the generated model.
    """
    payload = {
        "input_image": reactor_encode_image(reactor_input_image_path),
        "model_id": reactor_model_id,
    }

    response = requests.post(f"{reactor_API_URL}/reactor/image", json=payload)
    if response.status_code == 200:
        data = response.json()
        reactor_result_image_base64 = data.get("output_image")
        return Image.open(BytesIO(base64.b64decode(reactor_result_image_base64)))
    else:
        print(f"Error: {response.text}")
        return None

def reactor_run_img2img(reactor_input_image_path, reactor_prompt, reactor_denoising_strength=0.75):
    """
    Run img2img using AUTOMATIC1111 API with the replaced face.
    """
    payload = {
        "init_images": [reactor_encode_image(reactor_input_image_path)],
        "prompt": reactor_prompt,
        "denoising_strength": reactor_denoising_strength,
        "sampler_index": "Euler a"
    }

    response = requests.post(f"{reactor_API_URL}/sdapi/v1/img2img", json=payload)
    if response.status_code == 200:
        data = response.json()
        reactor_result_image_base64 = data['images'][0]
        return Image.open(BytesIO(base64.b64decode(reactor_result_image_base64)))
    else:
        print(f"Error: {response.text}")
        return None
