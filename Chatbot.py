import openai
import json
import os
from dotenv import load_dotenv

#load env
load_dotenv()

# Set your OpenAI API key here
openai_api_key = os.getenv("OPENAI_API_KEY")

CHAT_HISTORY_FILE = "chat_history.json"

def get_chatbot_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content']

def save_chat_history(messages):
    """Save the chat history to a JSON file."""
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(messages, file, indent=4)
    print("\n💾 Chat history saved!")

def load_chat_history():
    """Load chat history if it exists."""
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as file:
            messages = json.load(file)
        print("📂 Previous chat history loaded.")
        return messages
    return []

def main():
    print("🤖 Welcome to the AI-Powered Chatbot with Memory!")
    print("Type 'exit' to quit or 'clear' to reset memory.\n")
    
    # Load previous messages if available
    messages = load_chat_history()
    
    # If new session, ask for persona
    if not messages:
        persona = input("Set the chatbot persona (e.g., formal, casual, playful): ")
        messages.append({"role": "system", "content": f"You are a {persona} chatbot."})

    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            save_chat_history(messages)
            print("👋 Exiting the chatbot. Goodbye!")
            break
        
        elif user_input.lower() == 'clear':
            messages = []
            persona = input("Reset persona (e.g., formal, casual, playful): ")
            messages.append({"role": "system", "content": f"You are a {persona} chatbot."})
            if os.path.exists(CHAT_HISTORY_FILE):
                os.remove(CHAT_HISTORY_FILE)
            print("🧹 Chat memory cleared!")
            continue

        # Add user input
        messages.append({"role": "user", "content": user_input})
        
        # Get chatbot response
        response = get_chatbot_response(messages)
        messages.append({"role": "assistant", "content": response})
        
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    main()
