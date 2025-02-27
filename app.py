import gradio as gr
import requests


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
        
def gen_automatic():
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

def gen_civitai():
    civitai = gr.Blocks()
    with civitai:
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox()
                neg_prompt = gr.Textbox()
                civitai_submit = gr.Button()
            with gr.Column():
                civitai_output = gr.Gallery()
    return civitai

def gen_canva():
    t_interface = gr.TabbedInterface([gen_automatic(), gen_civitai()], ["Automatic", "Civitai"])
    return t_interface

iface = gen_canva()
iface.launch()
