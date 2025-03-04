from  pkg.globals import *


def apply_loras(prompt, selected_loras):
    if not selected_loras:
        return prompt  # Avoid modifying prompt if no LoRAs are selected
    
    lora_formats = []
    custom_words = []
    
    for lora in selected_loras:
        lora_data = LORA_CONFIG.get(lora)
        if lora_data:
            lora_formats.append(lora_data["format"])
            custom_words.append(lora_data["custom_wording"])
    
    prompt += f", {' '.join(custom_words)}" if custom_words else ""
    return f"{prompt} {' '.join(lora_formats)}".strip()