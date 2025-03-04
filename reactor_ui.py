import gradio as gr
from pkg.reactor_api import reactor_generate_facemodel, reactor_replace_face, reactor_run_img2img

def reactor_pipeline(reactor_reference_image, reactor_input_image, reactor_prompt, reactor_denoising_strength):
    """
    Full ReActor pipeline: Generate a model, replace the face, and refine the image.
    """
    # Save input images
    reactor_reference_image_path = "reactor_reference.jpg"
    reactor_input_image_path = "reactor_input.jpg"
    reactor_reference_image.save(reactor_reference_image_path)
    reactor_input_image.save(reactor_input_image_path)

    # Generate face model
    reactor_model_id = reactor_generate_facemodel(reactor_reference_image_path)
    if not reactor_model_id:
        return "Error generating face model!", None, None

    # Replace face
    reactor_face_replaced_img = reactor_replace_face(reactor_input_image_path, reactor_model_id)
    if not reactor_face_replaced_img:
        return "Error replacing face!", None, None

    # Run img2img for final refinement
    reactor_final_img = reactor_run_img2img(reactor_input_image_path, reactor_prompt, reactor_denoising_strength)
    if not reactor_final_img:
        return "Error enhancing image!", reactor_face_replaced_img, None

    return "Success!", reactor_face_replaced_img, reactor_final_img

# Gradio UI
with gr.Blocks() as reactor_ui:
    gr.Markdown("# 🎭 ReActor AI - Face Replacement & Image Enhancement")

    with gr.Row():
        reactor_reference_image = gr.Image(type="pil", label="Reference Face Image")
        reactor_input_image = gr.Image(type="pil", label="Input Image (Face to Replace)")

    reactor_prompt = gr.Textbox(label="Enhancement Prompt", value="a cinematic portrait")
    reactor_denoising_strength = gr.Slider(0.1, 1.0, value=0.75, label="Denoising Strength")

    reactor_output_status = gr.Textbox(label="Status", interactive=False)
    reactor_output_face = gr.Image(type="pil", label="Face-Replaced Image", interactive=False)
    reactor_output_final = gr.Image(type="pil", label="Final Enhanced Image", interactive=False)

    reactor_run_button = gr.Button("Run ReActor Pipeline")

    reactor_run_button.click(
        reactor_pipeline,
        inputs=[reactor_reference_image, reactor_input_image, reactor_prompt, reactor_denoising_strength],
        outputs=[reactor_output_status, reactor_output_face, reactor_output_final],
    )

# Launch UI
if __name__ == "__main__":
    reactor_ui.launch()
