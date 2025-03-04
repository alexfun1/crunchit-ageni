import sys
import json
import os
#global CONFIG_FILE, LORA_CONFIG, RESOLUTIONS, AUTOMATIC1111_URL, AVAILABLE_SAMPLERS, NEG_PROMPT


# Load Configuration
def load_conf(config):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("[ERROR] config.json not found!")
        sys.exit(1)

    # Extract LoRA and Automatic1111 settings
    
    return config

CONFIG_FILE=os.environ['CHAT_CONFIG'] 
config = load_conf(CONFIG_FILE)
LORA_CONFIG = {lora["description"]: lora for lora in config.get("loras", [])}
RESOLUTIONS = {resolutions["label"]: resolutions for resolutions in config.get("resolutions", [])}
AUTOMATIC1111_URL = config["automatic1111"]["url"]
AUTOMATIC1111_MODELS = config["automatic1111"]["models"]
AVAILABLE_SAMPLERS = config["automatic1111"]["samplers"]
NEG_PROMPT = config["negative_prompt"]

#CONFIG_FILE = "config.json"
#try:
#    with open(CONFIG_FILE, "r") as f:
#        config = json.load(f)
#except FileNotFoundError:
#    print("[ERROR] config.json not found!")
#    sys.exit(1)
#
## Extract LoRA and Automatic1111 settings
#LORA_CONFIG = {lora["description"]: lora for lora in config.get("loras", [])}
#RESOLUTIONS = {resolutions["label"]: resolutions for resolutions in config.get("resolutions", [])}
#AUTOMATIC1111_URL = config["automatic1111"]["url"]
#AVAILABLE_SAMPLERS = config["automatic1111"]["samplers"]
#NEG_PROMPT = config["negative_prompt"]