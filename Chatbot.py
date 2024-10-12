import openai

# Set your OpenAI API key here
openai.api_key = 'YOUR_API_KEY'

def get_chatbot_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content']

def main():
    print("Welcome to the AI-Powered Chatbot!")
    print("Type 'exit' to quit the chat.")
    
    # Initialize message history
    messages = []

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Exiting the chatbot. Goodbye!")
            break
        
        # Add the user message to the history
        messages.append({"role": "user", "content": user_input})
        
        # Get the chatbot response
        response = get_chatbot_response(messages)
        
        # Add the chatbot's response to the history
        messages.append({"role": "assistant", "content": response})
        
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    main()
