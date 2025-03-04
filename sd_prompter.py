import json
import gradio as gr

# Load prompt structure from external JSON file
def load_prompt_structure():
    with open("prompt_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Save updated prompt structure to JSON file
def save_prompt_structure(data):
    with open("prompt_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Load data from JSON
PROMPT_DATA = load_prompt_structure()

# Function to generate SD prompt string based on selected values
def build_prompt(subject, descriptions, positions):
    """Creates an ordered prompt string from selected dropdown values."""
    
    ordered_prompt = []

    # Add main subject
    if subject:
        ordered_prompt.append(subject)

    # Add additional descriptions if any
    if descriptions:
        ordered_prompt.append(", ".join(descriptions))

    # Add positioning if any
    if positions:
        ordered_prompt.append(", ".join(positions))

    return " | ".join(ordered_prompt) if ordered_prompt else "No prompt selected."

# Function to update Additional Descriptions and Positioning options dynamically
def update_options(selected_subject):
    """Updates additional descriptions and positioning based on the selected subject."""
    if not selected_subject:
        return gr.update(choices=[], value=[]), gr.update(choices=[], value=[])

    additional_descriptions = PROMPT_DATA["AdditionalDescriptions"].get(selected_subject, [])
    positioning = PROMPT_DATA["Positioning"].get(selected_subject, [])

    return gr.update(choices=additional_descriptions, value=[]), gr.update(choices=positioning, value=[])

# Gradio UI
with gr.Blocks() as sd_prompt_ui:
    gr.Markdown("# 🎨 Stable Diffusion Prompt Builder with Dynamic Additional Descriptions & Positioning")

    # Subject Dropdown (Single-Select)
    subject_dropdown = gr.Dropdown(
        choices=list(PROMPT_DATA["Subject"].keys()), 
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

    # Textbox to display the built prompt
    prompt_output = gr.Textbox(label="Generated SD Prompt", interactive=False, lines=2)

    # Function to handle updating descriptions & positioning dynamically
    subject_dropdown.change(update_options, inputs=[subject_dropdown], outputs=[additional_description_dropdown, positioning_dropdown])

    # Function to update the final SD prompt string
    def update_prompt(*values):
        return build_prompt(*values)

    # Link all dropdown selections to update the final prompt
    subject_dropdown.change(update_prompt, inputs=[subject_dropdown, additional_description_dropdown, positioning_dropdown], outputs=[prompt_output])
    additional_description_dropdown.change(update_prompt, inputs=[subject_dropdown, additional_description_dropdown, positioning_dropdown], outputs=[prompt_output])
    positioning_dropdown.change(update_prompt, inputs=[subject_dropdown, additional_description_dropdown, positioning_dropdown], outputs=[prompt_output])

# Run Gradio UI
if __name__ == "__main__":
    sd_prompt_ui.launch()
