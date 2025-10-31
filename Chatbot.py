# ------------------- IMPORTS -------------------
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from datetime import datetime
import json
import os
import random
import pyfiglet
import emoji
import time
import pyttsx3
from textblob import TextBlob
import requests

# ------------------- SETUP -------------------
load_dotenv()  # Load .env
API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_PERSONALITY = os.getenv("DEFAULT_PERSONALITY", "witty")
client = OpenAI(api_key=API_KEY)

console = Console()
users_file = "users_chat_history.json"

# Text-to-speech engine
tts_engine = pyttsx3.init()

# ------------------- LOAD USER DATA -------------------
if os.path.exists(users_file):
    with open(users_file, "r") as f:
        all_users_history = json.load(f)
else:
    all_users_history = {}

# ------------------- HELPER FUNCTIONS -------------------

def current_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

def gpt_response(user_input, conversation_history, mode="chat", personality="witty"):
    conversation_history.append({"role": "user", "content": user_input})

    personalities = {
        "witty": "You are witty, humorous, and use light emojis and jokes appropriately.",
        "professional": "You are professional, clear, and concise, with minimal emojis.",
        "fun": "You are playful, fun, and love emojis and ASCII art.",
        "friendly": "You are warm, friendly, and engaging with positive language."
    }

    system_msg = {
        "chat": personalities.get(personality, personalities["witty"]),
        "summarize": "Summarize the user's input concisely.",
        "explain": "Explain concepts clearly and simply.",
        "code": "Provide working code examples when appropriate."
    }.get(mode, personalities.get(personality, personalities["witty"]))

    temp_history = [{"role": "system", "content": system_msg}] + conversation_history[1:]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=temp_history
    )

    reply = response.choices[0].message.content
    reply_with_emoji = auto_emoji(reply)
    conversation_history.append({"role": "assistant", "content": reply_with_emoji})

    # Speak the reply
    tts_engine.say(reply_with_emoji)
    tts_engine.runAndWait()

    return reply_with_emoji

def display_conversation(conversation_history):
    console.print("\n[bold cyan]--- 💬 Conversation History ---[/bold cyan]")
    for msg in conversation_history[1:]:
        role = "You" if msg["role"] == "user" else "Chatbot 🤖"
        now = datetime.now().strftime("%H:%M:%S")
        console.print(f"[dim]{now}[/dim] [bold green]{role}:[/bold green] {msg['content']}")

# ------------------- FUN FEATURES -------------------

fun_facts = [
    "Honey never spoils 🍯",
    "Bananas are berries, but strawberries aren't 🍌🍓",
    "Octopuses have three hearts 🐙❤️❤️❤️",
    "A group of flamingos is called a 'flamboyance' 🦩🔥"
]

ascii_reactions = {
    "happy": "^_^",
    "thinking": "o_O",
    "surprised": ":O",
    "wink": ";)"
}

def random_fun_fact():
    return random.choice(fun_facts)

def ascii_art(text):
    return pyfiglet.figlet_format(text)

def emoji_message(msg):
    return emoji.emojize(msg)

def auto_emoji(text):
    keywords = {
        "happy": "😄",
        "sad": "😢",
        "love": "❤️",
        "wow": "😲",
        "fun": "🎉",
        "game": "🎮",
        "thanks": "🙏",
        "yes": "👍",
        "no": "❌"
    }
    for word, em in keywords.items():
        if word in text.lower():
            text += " " + em
    return text

def react_ascii(emotion):
    if emotion in ascii_reactions:
        console.print(f"[magenta]{ascii_reactions[emotion]}[/magenta]")
        time.sleep(1)

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return "happy"
    elif polarity < -0.3:
        return "sad"
    else:
        return "thinking"

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=3"
        res = requests.get(url)
        return res.text
    except Exception as e:
        return f"Could not fetch weather: {e}"

# ------------------- SAVE USER HISTORY -------------------
def save_user_history(user_name, conversation_history):
    all_users_history[user_name] = conversation_history
    with open(users_file, "w") as f:
        json.dump(all_users_history, f, indent=4)

# ------------------- MAIN LOOP -------------------
def main():
    console.print(Panel(f"[bold magenta]{current_greeting()}! Welcome to the GPT-Powered Chatbot![/bold magenta]\n"
                        "Commands: 'exit', 'history', 'fact', 'ascii', 'emoji', 'gpt', 'weather', 'switch_user'\n"
                        "GPT Modes: chat, summarize, explain, code", expand=False))

    user_name = Prompt.ask("Enter your name")
    personality = Prompt.ask(
        "Choose assistant personality: witty, professional, fun, friendly",
        default=DEFAULT_PERSONALITY
    )

    conversation_history = all_users_history.get(user_name, [
        {"role": "system", "content": f"You are a {personality} assistant who loves to help users."}
    ])

    while True:
        user_input = Prompt.ask(f"\n[bold green]{user_name}[/bold green]")

        if not user_input:
            continue

        command = user_input.lower()

        if command == "exit":
            save_user_history(user_name, conversation_history)
            console.print(f"[bold red]👋 Goodbye {user_name}! Conversation saved.[/bold red]")
            break
        elif command == "history":
            display_conversation(conversation_history)
            continue
        elif command == "fact":
            console.print(Panel(random_fun_fact(), title="🎉 Fun Fact"))
            continue
        elif command == "ascii":
            text = Prompt.ask("Enter text for ASCII art")
            console.print(f"[cyan]{ascii_art(text)}[/cyan]")
            continue
        elif command == "emoji":
            msg = Prompt.ask("Enter text to add emojis")
            console.print(emoji_message(msg))
            continue
        elif command == "gpt":
            mode = Prompt.ask("Choose GPT mode: chat, summarize, explain, code", default="chat")
            user_text = Prompt.ask("Enter your text for GPT")
            response = gpt_response(user_text, conversation_history, mode, personality)
            console.print(Markdown(f"**Chatbot 🤖:** {response}"))
            react_ascii(random.choice(list(ascii_reactions.keys())))
            continue
        elif command == "weather":
            city = Prompt.ask("Enter city for weather")
            console.print(Panel(get_weather(city), title=f"🌤 Weather in {city}"))
            continue
        elif command == "switch_user":
            save_user_history(user_name, conversation_history)
            user_name = Prompt.ask("Enter new user name")
            conversation_history = all_users_history.get(user_name, [
                {"role": "system", "content": f"You are a {personality} assistant who loves to help users."}
            ])
            console.print(f"[bold cyan]Switched to user: {user_name}[/bold cyan]")
            continue

        # Normal conversation with sentiment-aware reaction
        sentiment = analyze_sentiment(user_input)
        response = gpt_response(user_input, conversation_history, mode="chat", personality=personality)
        console.print(Markdown(f"**Chatbot 🤖:** {response}"))
        react_ascii(sentiment)

# ------------------- RUN -------------------
if __name__ == "__main__":
    main()
