import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import config


def get_azure_credential():
    use_mi_auth = config.USE_MI_AUTH

    if use_mi_auth:
        mi_client_id = config.MI_CLIENT_ID
        return ManagedIdentityCredential(
            client_id=mi_client_id
        )
    return DefaultAzureCredential()

def load_prompt_string(prompt_path: str) -> str:
    dir = os.path.dirname(os.path.abspath(__file__)) # directory of current file
    prompt_path = os.path.join(dir, prompt_path) # dir += prompts/prompt_name.txt

    try:
        with open(prompt_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Prompt file not found: {prompt_path}")
        return None
