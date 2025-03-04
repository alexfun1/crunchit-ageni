import torch
import gradio as gr
import signal
import gc
import sys
from transformers import CLIPTokenizer
from pathlib import Path
from pkg.loras import *
import  pkg.globals as globals
import pkg.resolutions as resolutions
from pkg.automatic import *
from pkg.local import *
import base64
import helpers as h

if not load_conf("/home/fun/Projects/crunchit-ageni/config.json"):
    sys.exit(1)


# Gradio UI
with gr.Blocks() as gallery:
    image_gallery_ui = gr.Gallery(label="Generated Images")

with gr.Blocks() as settings:
    with gr.Row():
        with gr.Column():
            with gr.Row():
                platform_selector = gr.Radio(["Local (Fluently-XL-Final)", "Automatic1111"], label="Select Generation Platform", value="Automatic1111")
                model_dropdown = gr.Dropdown(choices=list(AUTOMATIC1111_MODELS.keys()), label="Select Model")
                model_dropdown.change(change_model, inputs=model_dropdown)
            with gr.Row():
                lora_selector = gr.CheckboxGroup(choices=list(globals.LORA_CONFIG.keys()), label="Select LoRAs to Apply")
            with gr.Row():
                resolution_selector = gr.Radio(choices=list(globals.RESOLUTIONS.keys()), label="Select Resolution",value=list(globals.RESOLUTIONS.keys())[0])
            with gr.Row():
                adetailer_toggle = gr.Checkbox(label="Enable ADetailer", value=False)
        with gr.Column():
            with gr.Row():
                reactor_toggle = gr.Checkbox(label="Enable ReActor Plugin", value=False)
                reactor_method = gr.Radio(["Image", "Model"], label="Select ReActor Method", value="Image")
                reactor_models = gr.Dropdown(choices=["model_1", "model_2"], label="Select ReActor Face Model")
            with gr.Row():
                reactor_face = gr.Image(label="Reference Face Image", interactive=True)
                reactor_base64_output = gr.Textbox(label="Base64 Encoded Reference Face", visible=False)
        with gr.Column():
            with gr.Row():
                pose_enabler = gr.Checkbox(label="Pose map enabled", info="Enable/Disable pose mapping")    #(label="Pose", choices=["true", "false"], value="false")
            with gr.Row():
                pose = gr.Gallery(label="Poses", interactive=True, value=h.get_depth_images(), columns=4, visible=True)
                pose_base64 = gr.Textbox(label="Base64 Encoded Original Image", interactive=False, visible=False)

    reactor_face.upload(h.convert_image_to_base64, inputs=[reactor_face], outputs=[reactor_base64_output])

    def on_pose_click(selection: gr.SelectData):
        return h.encode_image(selection.value['image']['path'])

    pose.select(on_pose_click, inputs=None, outputs=[pose_base64])
                

with gr.Blocks() as generator:
    with gr.Row():
        with gr.Column():
            with gr.Row():
                output_image = gr.Image(label="Generated Image", height=512, width=768, interactive=False)
            with gr.Row():
                prompt_input = gr.Textbox(label="Prompt")
                generate_button = gr.Button("Generate Image")
        
        #with gr.Column():
        #    with gr.Row():
        #        platform_selector = gr.Radio(["Local (Fluently-XL-Final)", "Automatic1111"], label="Select Generation Platform", value="Automatic1111")
        #        model_dropdown = gr.Dropdown(choices=list(AUTOMATIC1111_MODELS.keys()), label="Select Model")
        #        model_dropdown.change(change_model, inputs=model_dropdown)
        #    with gr.Row():
        #        lora_selector = gr.CheckboxGroup(choices=list(globals.LORA_CONFIG.keys()), label="Select LoRAs to Apply")
        #    with gr.Row():
        #        resolution_selector = gr.Radio(choices=list(globals.RESOLUTIONS.keys()), label="Select Resolution",value=list(globals.RESOLUTIONS.keys())[0])
        #    with gr.Row():
        #        reactor_toggle = gr.Checkbox(label="Enable ReActor Plugin", value=False)
        #        adetailer_toggle = gr.Checkbox(label="Enable ADetailer", value=False)
            #with gr.Row():
            #    sampler_selector = gr.Radio(choices=AVAILABLE_SAMPLERS, label="Select Sampler", value=AVAILABLE_SAMPLERS[0])
            #with gr.Row():
            #    models = gr.Textbox(label="Models", value=get_models())
            #    options = gr.Textbox(label="Options", value=get_options())
    
    generate_button.click(h.generate_image, inputs=[prompt_input, platform_selector, lora_selector, resolution_selector, reactor_toggle, adetailer_toggle, model_dropdown, pose_base64, pose_enabler, reactor_base64_output, reactor_method, reactor_models], outputs=[output_image, image_gallery_ui])

with gr.Blocks() as edit:
    gr.Markdown("# Image-to-Image Generation via Automatic1111 API")
    
    with gr.Row():
        image_input = gr.Image(label="Upload Image")
        #model_dropdown = gr.Dropdown(choices=["cyberrealisticPony_v8", "dreamshaperXL_v21TurboDPMSDE", "duchaitenPonyReal_v20", "epicrealism_naturalSinRC1VAE", "Juggernaut_X_RunDiffusion_Hyper", "milftoonMix_v10", "ponimilfmix_lightning", "ponyDiffusionV6XL_v6StartWithThisOne"], label="Select Model")
    
    editor_prompt_input = gr.Textbox(label="Prompt")
    strength_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.75, label="Strength")
    edit_button = gr.Button("Generate Image")
    editor_output_image = gr.Image(label="Generated Image")
    
    edit_button.click(img2img, inputs=[image_input, editor_prompt_input, strength_slider, model_dropdown], outputs=editor_output_image)

## Prompt editor
# Function to update Additional Descriptions and Positioning options dynamically
def update_options(selected_subject):
    """Updates additional descriptions and positioning based on the selected subject."""
    if not selected_subject:
        return gr.update(choices=[], value=[]), gr.update(choices=[], value=[])

    additional_descriptions = h.PROMPT_DATA["AdditionalDescriptions"].get(selected_subject, [])
    positioning = h.PROMPT_DATA["Positioning"].get(selected_subject, [])

    return gr.update(choices=additional_descriptions, value=[]), gr.update(choices=positioning, value=[])

with gr.Blocks() as sd_prompt_ui:
    gr.Markdown("# 🎨 Stable Diffusion Prompt Builder with Dynamic Additional Descriptions & Positioning")

    # Subject Dropdown (Single-Select)
    subject_dropdown = gr.Dropdown(
        choices=list(h.PROMPT_DATA["Subject"].keys()), 
        label="Select Subject", 
        multiselect=False,  # Only one subject can be selected at a time
        value=None,  # No default value
        interactive=True
    )

    # Additional Description Dropdown (Empty initially, updates dynamically)
    additional_description_dropdown = gr.Dropdown(
        choices=[], label="Select Additional Description", multiselect=True, interactive=True
    )

    # Positioning Dropdown (Empty initially, updates dynamically)
    positioning_dropdown = gr.Dropdown(
        choices=[], label="Select Positioning", multiselect=True, interactive=True
    )

    # Function to handle updating descriptions & positioning dynamically
    subject_dropdown.change(update_options, inputs=[subject_dropdown], outputs=[additional_description_dropdown, positioning_dropdown])

    # Function to update the final SD prompt string
    def update_prompt(*values):
        return h.build_prompt(*values)

    # Link all dropdown selections to update the final prompt
    subject_dropdown.change(update_prompt, inputs=[subject_dropdown, additional_description_dropdown, positioning_dropdown], outputs=[prompt_input])
    additional_description_dropdown.change(update_prompt, inputs=[subject_dropdown, additional_description_dropdown, positioning_dropdown], outputs=[prompt_input])
    positioning_dropdown.change(update_prompt, inputs=[subject_dropdown, additional_description_dropdown, positioning_dropdown], outputs=[prompt_input])



main_iface = gr.TabbedInterface([
    generator,
    sd_prompt_ui,
    settings,
    edit,
    gallery
],["Generator", "Prompt Helper", "Settings", "Edit Image", "Gallery"])

# Run the app with cleanup on exit
try:
    main_iface.launch(server_port=7880, debug=True)
except KeyboardInterrupt:
    h.cleanup()
    sys.exit(0)