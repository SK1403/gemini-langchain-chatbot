#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Configuration module encapsulating environment variables, Google Cloud project
#       and region defaults, Gemini model selections, and inference hyperparameters.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 14/08/2024          Saddam Khan        Initial implementation
# 10/09/2024          Saddam Khan        Added dynamic model and hyperparameter settings
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

@dataclass
class Settings:
    """
    Explanation: Dataclass holding application configuration attributes and model parameters
    :param  project_id str: Default GCP Project ID resolved from environment
    :param  location str: Default GCP region for Vertex AI endpoints
    :param  model_name str: Target Gemini model identifier
    :param  temperature float: Default temperature setting for LLM responses
    :param  max_output_tokens int: Upper bound of token generation per query
    :param  system_instruction str: Default system persona prompt
    """
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    model_name: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
    system_instruction: str = os.getenv(
        "SYSTEM_INSTRUCTION",
        "You are a helpful, knowledgeable, and concise AI assistant powered by Gemini on Google Cloud Platform."
    )

settings = Settings()
