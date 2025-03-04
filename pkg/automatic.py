from pkg.globals import *
from pkg.loras import apply_loras
from pkg.resolutions import apply_resolution
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import base64


def generate_with_automatic1111(prompt, selected_loras, selected_resolutions, use_reactor, use_adetailer, gallery_folder, image_gallery, model_name, pose_base64, use_pose, reactor_img_base64, ops_22, reactor_models):
    """Submit request to Automatic1111 API"""
    try:
        
        # Apply LoRAs
        if selected_loras:
            prompt = apply_loras(prompt, selected_loras)

        if selected_resolutions:
            width, height = apply_resolution(selected_resolutions)
        else:
            width, height = 64, 64

        # Apply ReActor
        if use_reactor:
            prompt = f"{prompt}, (reactor:1.2)"

        # Apply ADetailer
        if use_adetailer:
            prompt = f"{prompt}, (adetailer:1.2)"
        prompt 
        model = AUTOMATIC1111_MODELS[model_name]
        
        payload = {
            "prompt": model["prompt"]+" " + prompt,
            "negative_prompt": model["negative_prompt"],
            "width": width,
            "height": height,
            "steps": model["steps"],
            "cfg_scale": model["guidance"],
            #"hr_scale": 2,
            #"hr_upscaler": "Latent",
            "sampler_name": model["sampler"],
            "scheduler": model["scheduler"],
            "alwayson_scripts": {
            }
        }

        #Using Pose ControlNet?
        if use_pose:
            payload["alwayson_scripts"]["controlnet"] = {
                "args": [
                  {
                    "enabled": "true",
                    "image": pose_base64,
                    "model": model["pose_model"],
                    "weight": 0.5
                  }
                ]
              }
        
        #reactor
        if use_reactor:
            payload["alwayson_scripts"]["reactor"] = {
                "args": reactor_alwayson(reactor_img_base64, ops_22)
            }

        response = requests.post(f"{AUTOMATIC1111_URL}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()

        result = response.json()
        if "images" in result:
            image_data = result["images"][0]
            image = Image.open(BytesIO(base64.b64decode(image_data)))

            img_path = gallery_folder / f"generated_{len(image_gallery) + 1}.png"
            image.save(img_path)

            image_gallery.append(img_path)

            return image, [str(img) for img in image_gallery]
        else:
            return None, image_gallery
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}", image_gallery

#img2img
def convert_numpy_to_pil(image):
    """Convert a numpy array to a PIL Image."""
    if isinstance(image, np.ndarray):
        return Image.fromarray(image.astype('uint8'))
    return image

def img2img(image, prompt, strength, model):
    """Sends an image-to-image request to the Automatic1111 API."""
    if image is None:
        return "Error: No image provided."
    
    image = convert_numpy_to_pil(image)
    
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    payload = {
        "init_images": [image_b64],
        "prompt": prompt,
        "strength": strength,
        "sampler_index": "Euler a",
        "steps": 30,
        "cfg_scale": 7.5,
        "width": image.width,
        "height": image.height,
        "model": model
    }
    
    try:
        response = requests.post(f"{AUTOMATIC1111_URL}/sdapi/v1/img2img", json=payload)
        response.raise_for_status()
        result = response.json()
        if "images" in result:
            img_data = base64.b64decode(result["images"][0])
            return Image.open(BytesIO(img_data))
        else:
            return "Error: No image received from API."
    except Exception as e:
        return f"Error: {str(e)}"
    
#change model 
def get_models():
    response = requests.get(f"{AUTOMATIC1111_URL}/sdapi/v1/sd-models")
    response.raise_for_status()
    return response.json()
    models = result["models"]

def get_options():
    response = requests.get(f"{AUTOMATIC1111_URL}/sdapi/v1/options")
    response.raise_for_status()
    return response.json()

def get_model_parameters(model_name):
    return AUTOMATIC1111_MODELS.get(model_name, "Model not found")

def change_model(model_name):
    params = get_model_parameters(model_name)
    opt = requests.get(url=f'{AUTOMATIC1111_URL}/sdapi/v1/options')
    opt_json = opt.json()
    opt_json['sd_model_checkpoint'] = params['name']
    requests.post(url=f'{AUTOMATIC1111_URL}/sdapi/v1/options', json=opt_json)
    # Checking result
    response = requests.get(url=f'{AUTOMATIC1111_URL}/sdapi/v1/sd-models')
    #return response.json()
    #return AUTOMATIC1111_MODELS.get(model_name, "Model not found")

def reactor_alwayson(img_base64, ops_22):
    args=[
    img_base64, #img_base64, #0
    True, #1 Enable ReActor
    '0', #2 Comma separated face number(s) from swap-source image
    '0', #3 Comma separated face number(s) for target image (result)
    '/home/fun/AI-Platforms/stable-diffusion-webui-forge/models/insightface/inswapper_128.onnx', #4 model path
    'CodeFormer', #4 Restore Face: None; CodeFormer; GFPGAN
    1, #5 Restore visibility value
    True, #7 Restore face -> Upscale
    '4x_NMKD-Superscale-SP_178000_G', #8 Upscaler (type 'None' if doesn't need), see full list here: http://127.0.0.1:7860/sdapi/v1/script-info -> reactor -> sec.8
    1.5, #9 Upscaler scale value
    1, #10 Upscaler visibility (if scale = 1)
    False, #11 Swap in source image
    True, #12 Swap in generated image
    1, #13 Console Log Level (0 - min, 1 - med or 2 - max)
    0, #14 Gender Detection (Source) (0 - No, 1 - Female Only, 2 - Male Only)
    0, #15 Gender Detection (Target) (0 - No, 1 - Female Only, 2 - Male Only)
    False, #16 Save the original image(s) made before swapping
    0.8, #17 CodeFormer Weight (0 = maximum effect, 1 = minimum effect), 0.5 - by default
    False, #18 Source Image Hash Check, True - by default
    False, #19 Target Image Hash Check, False - by default
    "CUDA", #20 CPU or CUDA (if you have it), CPU - by default
    True, #21 Face Mask Correction
    ops_22, #22 Select Source, 0 - Image, 1 - Face Model, 2 - Source Folder
    "OlgaTuned.safetensors", #23 Filename of the face model (from "models/reactor/faces"), e.g. elena.safetensors, don't forger to set #22 to 1
    "C:\PATH_TO_FACES_IMAGES", #24 The path to the folder containing source faces images, don't forger to set #22 to 2
    None, #25 skip it for API
    True, #26 Randomly select an image from the path
    True, #27 Force Upscale even if no face found
    0.6, #28 Face Detection Threshold
    2, #29 Maximum number of faces to detect (0 is unlimited)
    ]
    return args