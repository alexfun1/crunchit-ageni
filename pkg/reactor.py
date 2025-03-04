import requests
import base64
import json
from io import BytesIO
from PIL import Image

# Set AUTOMATIC1111 API URL
API_URL = "http://127.0.0.1:7860"  # Change if necessary

def encode_image(image_path):
    """Encode image as base64 for API request."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def generate_facemodel(reference_image_path):
    """
    Generate a face model from a reference image using ReActor API.
    """
    payload = {
        "face_image": encode_image(reference_image_path),
        "model_name": "custom_face",  # Change this if needed
    }
    
    response = requests.post(f"{API_URL}/sdapi/v1/reactor/generate", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"Face model generated: {data}")
        return data.get("model_id")  # Return generated model ID
    else:
        print(f"Error: {response.text}")
        return None

def replace_face(input_image_path, model_id):
    """
    Replace face in an image using the generated model.
    """
    payload = {
        "input_image": encode_image(input_image_path),
        "model_id": model_id,
    }
    
    response = requests.post(f"{API_URL}/sdapi/v1/reactor/replace", json=payload)
    if response.status_code == 200:
        data = response.json()
        result_image_base64 = data.get("output_image")
        return Image.open(BytesIO(base64.b64decode(result_image_base64)))
    else:
        print(f"Error: {response.text}")
        return None

def run_txt2img(prompt, width=512, height=512, steps=30, cfg_scale=7):
    """
    Run txt2img generation using AUTOMATIC1111 API.
    """
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "sampler_index": "Euler a"
    }

    response = requests.post(f"{API_URL}/sdapi/v1/txt2img", json=payload)
    if response.status_code == 200:
        data = response.json()
        result_image_base64 = data['images'][0]
        return Image.open(BytesIO(base64.b64decode(result_image_base64)))
    else:
        print(f"Error: {response.text}")
        return None

def run_img2img(input_image_path, prompt, denoising_strength=0.75):
    """
    Run img2img using AUTOMATIC1111 API with the replaced face.
    """
    payload = {
        "init_images": [encode_image(input_image_path)],
        "prompt": prompt,
        "denoising_strength": denoising_strength,
        "sampler_index": "Euler a"
    }

    response = requests.post(f"{API_URL}/sdapi/v1/img2img", json=payload)
    if response.status_code == 200:
        data = response.json()
        result_image_base64 = data['images'][0]
        return Image.open(BytesIO(base64.b64decode(result_image_base64)))
    else:
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    reference_image = "face_reference.jpg"  # Path to reference image
    input_image = "input_face.jpg"  # Path to input image for face replacement
    output_face_replaced = "face_replaced.jpg"
    output_final = "final_result.jpg"

    # Generate the face model
    model_id = generate_facemodel(reference_image)

    if model_id:
        # Replace the face in the input image
        face_replaced_img = replace_face(input_image, model_id)
        if face_replaced_img:
            face_replaced_img.save(output_face_replaced)
            print(f"Face replaced image saved as {output_face_replaced}")

            # Run img2img on the replaced face to enhance
            final_img = run_img2img(output_face_replaced, prompt="a cinematic portrait")
            if final_img:
                final_img.save(output_final)
                print(f"Final enhanced image saved as {output_final}")
