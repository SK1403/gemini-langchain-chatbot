#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Streamlit interactive web user interface for Gemini Conversational Chatbot.
#       Provides dynamic GCP project/region selection, Gemini foundation model switching,
#       hyperparameter adjustments, real-time token streaming, and conversation reset.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 14/08/2024          Saddam Khan        Initial implementation
# 10/09/2024          Saddam Khan        Enhanced Vertex AI streaming and multi-turn session UI
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Explanation: Streamlit Web UI Application providing an interactive web interface for
             the Google Cloud Vertex AI Gemini Conversational Chatbot.
             Manages real-time parameter tuning, user session chat history,
             streaming tokens, and GCP authentication status verification.
:param None: Reads execution configuration from settings and runtime user inputs
:return None: Renders interactive web application in browser
"""

from typing import Tuple, Dict, Any
import streamlit as st
from chatbot import GeminiChatbot
from config import settings
from utils.auth import resolve_gcp_project, verify_adc

def init_page_config() -> None:
    """
    Explanation:
        Sets Streamlit page layout configuration including page title, browser favicon icon,
        and expanded wide layout mode for enterprise conversation display.

    :param None: Reads no input parameters.
    :return None: Configures Streamlit page display settings.
    """
    st.set_page_config(
        page_title="Gemini Chatbot (Vertex AI + LangChain)",
        page_icon="💬",
        layout="wide",
    )

def render_sidebar() -> Dict[str, Any]:
    """
    Explanation:
        Renders the sidebar navigation controls for GCP credentials status, project ID,
        region selection, Gemini foundation model picking, temperature tuning,
        system prompt customization, and session history reset.

    :param None: Reads user interactive inputs from Streamlit sidebar widgets.
    :return config Dict[str, Any]: Dictionary containing active user-selected configurations
        including 'gcp_project', 'gcp_region', 'model_choice', 'temperature', and 'system_prompt'.
    """
    with st.sidebar:
        st.header("⚙️ Model & GCP Settings")

        # ADC Check
        is_adc_valid, adc_project = verify_adc()
        if is_adc_valid:
            st.success(f"ADC Active: `{adc_project or 'Configured'}`")
        else:
            st.warning("⚠️ ADC not found. Run `gcloud auth application-default login`.")

        # Project & Region
        resolved_project = resolve_gcp_project(settings.project_id)
        gcp_project = st.text_input("GCP Project ID", value=resolved_project)
        gcp_region = st.selectbox(
            "GCP Location / Region",
            options=["us-central1", "europe-west1", "europe-west4", "asia-northeast1", "us-east4"],
            index=0,
        )

        # Model Selection
        model_choice = st.selectbox(
            "Gemini Model",
            options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
            index=0,
            help="gemini-1.5-flash: fast & cost-efficient\ngemini-1.5-pro: advanced reasoning & multimodal",
        )

        # Hyperparameters
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=settings.temperature,
            step=0.05,
        )

        # Custom System Instruction
        system_prompt = st.text_area(
            "System Instruction (Persona)",
            value=settings.system_instruction,
            height=100,
        )

        st.markdown("---")
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            if "bot" in st.session_state:
                st.session_state.bot.clear_history("streamlit_session")
            st.session_state.messages = []
            st.rerun()

        return {
            "gcp_project": gcp_project,
            "gcp_region": gcp_region,
            "model_choice": model_choice,
            "temperature": temperature,
            "system_prompt": system_prompt,
        }

def get_or_create_bot(
    model_choice: str,
    gcp_project: str,
    gcp_region: str,
    temperature: float,
    system_prompt: str,
) -> GeminiChatbot:
    """
    Explanation: Retrieves existing GeminiChatbot instance from session state or instantiates a new one
                 if model parameters, project, or prompt instructions have been reconfigured.
    :param  model_choice str: Selected Gemini model identifier
    :param  gcp_project str: Target GCP project ID
    :param  gcp_region str: Vertex AI geographical region
    :param  temperature float: Sampling temperature (0.0 to 1.0)
    :param  system_prompt str: Custom system instructions for the assistant
    :return bot GeminiChatbot: Initialized chatbot instance
    """
    bot_key = f"{model_choice}_{gcp_project}_{gcp_region}_{temperature}_{hash(system_prompt)}"
    if "current_bot_key" not in st.session_state or st.session_state.current_bot_key != bot_key:
        st.session_state.bot = GeminiChatbot(
            model_name=model_choice,
            project_id=gcp_project,
            location=gcp_region,
            temperature=temperature,
            system_instruction=system_prompt,
        )
        st.session_state.current_bot_key = bot_key
    return st.session_state.bot

def render_chat_interface(bot: GeminiChatbot, model_choice: str) -> None:
    """
    Explanation: Renders the chat header, conversation message log, user input prompt,
                 and handles streaming responses from Vertex AI with contextual error diagnostics.
    :param  bot GeminiChatbot: Active GeminiChatbot instance
    :param  model_choice str: Selected Gemini foundation model name
    :return None: Renders UI components to Streamlit
    """
    st.title("💬 Gemini Enterprise Chatbot")
    st.caption(f"Powered by **Vertex AI ({model_choice})**, **LangChain**, and **Python** on Google Cloud.")

    # Session message state for UI display
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display welcome message if empty
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("Hello! I am your AI assistant powered by Google Cloud Vertex AI and LangChain. How can I help you today?")

    # Render historical messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Chat Input
    if prompt := st.chat_input("Type your message here..."):
        # Append & display human message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Stream Assistant Response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                for chunk in bot.stream_chat(prompt, session_id="streamlit_session"):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")

                if full_response:
                    response_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    response_placeholder.warning("Received empty response from Gemini.")
            except Exception as e:
                err_text = str(e)
                if "BILLING_DISABLED" in err_text or "requires billing" in err_text:
                    response_placeholder.error(
                        f"💳 **Billing Required**\n\n"
                        f"Vertex AI requires a Billing Account linked to project **`{bot.project_id}`**.\n\n"
                        f"👉 [Click here to enable billing on {bot.project_id}](https://console.developers.google.com/billing/enable?project={bot.project_id})"
                    )
                elif "RESOURCE_USAGE_RESTRICTION_VIOLATED" in err_text:
                    response_placeholder.error(
                        f"🔒 **Policy Restriction**\n\n"
                        f"Project **`{bot.project_id}`** has an organization policy restricting Vertex AI.\n\n"
                        f"Please switch to a personal/sandbox project."
                    )
                else:
                    response_placeholder.error(f"⚠️ **Inference Error**: {err_text}")

def main() -> None:
    """
    Explanation:
        Main application orchestration function coordinating layout initialization,
        sidebar rendering, bot lifecycle management, and chat interaction.

    :param None: Reads execution configuration and coordinates Streamlit execution cycle.
    :return None: Executes Streamlit rendering lifecycle.
    """
    init_page_config()
    cfg = render_sidebar()
    bot = get_or_create_bot(
        model_choice=cfg["model_choice"],
        gcp_project=cfg["gcp_project"],
        gcp_region=cfg["gcp_region"],
        temperature=cfg["temperature"],
        system_prompt=cfg["system_prompt"],
    )
    render_chat_interface(bot=bot, model_choice=cfg["model_choice"])

if __name__ == "__main__":
    main()
