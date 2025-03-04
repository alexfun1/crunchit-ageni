import gradio as gr
import requests
import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config



def automatic_get_output(prompt, neg_prompt):
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    payload = {
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "steps": 20
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        images = result.get("images", [])
        return images
    else:
        response.raise_for_status()

def gen_image():
    automatic = gr.Blocks()
    with automatic:
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox()
                neg_prompt = gr.Textbox()
                automatic_submit = gr.Button()
            with gr.Column():
                automatic_output = gr.Gallery()
            
    return automatic

def get_user_personal_data(id):
    users_path = os.path.join(os.path.dirname(__file__), 'users.json')
    with open(users_path, 'r') as users_file:
        users = json.load(users_file)
    user_data = users.get(str(id), {})
    return user_data


def gen_user_mgmt_tab():
    civitai = gr.Blocks()
    with civitai:
        with gr.Row():
            with gr.Column():
                login = gr.Textbox()
                password = gr.Textbox()
                mana = gr.Textbox()
                buy_mana = gr.Button()
            with gr.Column():
                civitai_output = gr.Gallery()
    return civitai

def gen_canva():
    t_interface = gr.TabbedInterface([gen_automatic(), gen_user_mgmt_tab()], ["Automatic", "Civitai"])
    return t_interface


config = load_config()

iface = gen_canva()
iface.launch()
