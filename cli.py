#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Command-line interface (CLI) chat runner for Gemini LangChain Chatbot.
#       Validates Application Default Credentials (ADC), initializes interactive multi-turn
#       session, and provides terminal-based token streaming.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 14/08/2024          Saddam Khan        Initial implementation
# 10/09/2024          Saddam Khan        Added interactive terminal streaming and session loop
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
from chatbot import GeminiChatbot
from utils.auth import verify_adc

def main():
    """
    Explanation: Entrypoint for running interactive CLI conversation loop with Gemini
    :return None: Executes CLI loop until exit command or interruption
    """
    print("=" * 65)
    print("        Gemini + Vertex AI + LangChain Chatbot (CLI)")
    print("=" * 65)

    # 1. ADC Verification
    is_valid, project_info = verify_adc()
    if not is_valid:
        print("\n[!] WARNING: Google Application Default Credentials (ADC) not detected.")
        print("    Please authenticate by running: gcloud auth application-default login")
        print("    Details:", project_info)
        print("=" * 65)

    # 2. Initialize Bot
    try:
        bot = GeminiChatbot()
        project_display = bot.project_id or "(auto-detected via ADC)"
        print(f"[*] GCP Project: {project_display}")
        print(f"[*] GCP Region:  {bot.location}")
        print(f"[*] LLM Model:   {bot.model_name}")
        print(f"[*] Temperature: {bot.temperature}")
        print("\nCommands: type 'exit' or 'quit' to end, 'clear' to reset memory.")
        print("-" * 65)
    except Exception as e:
        print(f"[x] Error initializing chatbot: {e}")
        sys.exit(1)

    session_id = "cli_session"

    # 3. Chat Loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if user_input.lower() in ["clear", "reset"]:
                bot.clear_history(session_id)
                print("[*] Session history cleared.")
                continue

            if user_input.lower() in ["help"]:
                print("Available commands:")
                print("  clear / reset - Clear chat history for this session")
                print("  exit / quit   - Exit the CLI chatbot")
                continue

            print("\nGemini: ", end="", flush=True)
            for chunk in bot.stream_chat(user_input, session_id=session_id):
                print(chunk, end="", flush=True)
            print()

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n[x] Error during inference: {e}")

if __name__ == "__main__":
    main()
