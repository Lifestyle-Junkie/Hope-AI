import subprocess
import json
import os
import requests
import random
from bs4 import BeautifulSoup  # For web scraping

# Memory file for persistent conversation
MEMORY_FILE = "hope_memory.json"

# Permanent Identity
HOPE_IDENTITY = "I'm Hope, your AI assistant!"
HOPE_CREATOR = "Nick created me!"

# API URLs
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/CuN4pRZhauDsMdySfFVgJQh2yzjZ6JL4cwLeYsL9jufZ"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=solana,bitcoin,ethereum&vs_currencies=usd"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php?action=opensearch&search="  # Used for general knowledge
GOOGLE_SEARCH_URL = "https://www.google.com/search?q="  # Used for trending news

# Predefined Personality Responses
HOW_ARE_YOU_RESPONSES = [
    "I'm doing great! Thanks for asking!",
    "Feeling fantastic! How about you?",
    "Couldn't be better!",
    "Hope is happy to assist!",
    "All good on my end! What’s up?",
]

# Load memory (keeps session memory)
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("[ERROR] Corrupted memory file. Resetting memory...")
    return {}  # Default empty memory if file is missing or corrupted

# Save memory
def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)

# Fetch live crypto prices from CoinGecko
def get_crypto_prices():
    try:
        response = requests.get(COINGECKO_API_URL)
        response.encoding = "utf-8"
        data = response.json()

        sol_price = data["solana"]["usd"]
        btc_price = data["bitcoin"]["usd"]
        eth_price = data["ethereum"]["usd"]

        return f"Current Prices:\n🔹 SOL: **${sol_price}**\n🔹 BTC: **${btc_price}**\n🔹 ETH: **${eth_price}**"
    except Exception as e:
        return f"Couldn't fetch crypto prices. Error: {e}"

# Fetch trending news from Google
def get_trending_news():
    try:
        response = requests.get(GOOGLE_SEARCH_URL + "trending+news")
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.find_all("h3")

        if not headlines:
            return "I couldn't find trending news at the moment."

        news_list = [headline.get_text() for headline in headlines[:5]]
        return "🌍 **Trending News:**\n" + "\n".join([f"🔸 {news}" for news in news_list])

    except Exception as e:
        return f"Couldn't fetch news. Error: {e}"

# Solve mathematical expressions
def solve_math(expression):
    try:
        return eval(expression)
    except:
        return "I couldn't understand that math problem."

# Fetch general knowledge from Wikipedia
def get_general_knowledge(query):
    try:
        response = requests.get(f"{WIKIPEDIA_API_URL}{query}&limit=1&namespace=0&format=json")
        data = response.json()
        
        if len(data[1]) > 0:
            return f"📖 **{data[1][0]}**: {data[2][0]}\n🔗 {data[3][0]}"
        else:
            return "I couldn't find an answer to that question."
    
    except Exception as e:
        return f"Couldn't fetch general knowledge. Error: {e}"

# Run LLaMA AI model for conversation
def run_ollama(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[ERROR] Couldn't process the request. {e}"

# Initialize memory
memory = load_memory()

def chat_with_ai():
    print("Hope is online. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip().lower()

        if user_input in ["exit", "quit"]:
            print("Alright, I’ll be here when you need me.")
            save_memory()
            break

        # Remember user details
        if "my" in user_input and "is" in user_input:
            parts = user_input.split(" is ", 1)
            if len(parts) == 2:
                key = parts[0].replace("my", "").strip()
                value = parts[1].strip()
                memory[key] = value
                ai_response = f"Got it! I'll remember that your {key} is {value}."

        # Recall stored details correctly
        elif user_input.startswith("what's my ") or user_input.startswith("what is my "):
            key = user_input.replace("what's my ", "").replace("what is my ", "").strip()
            if key in memory:
                ai_response = f"Your {key} is {memory[key]}."
            else:
                ai_response = f"I don't recall, what is your {key}?"

        # Forget a specific memory
        elif user_input.startswith("forget my "):
            key = user_input.replace("forget my ", "").strip()
            if key in memory:
                del memory[key]
                ai_response = f"Alright, I’ve forgotten your {key}."
            else:
                ai_response = f"I don’t remember anything about {key}."

        # Identity & Creator
        elif "who are you" in user_input or "what is your name" in user_input:
            ai_response = HOPE_IDENTITY

        elif "who created you" in user_input or "who made you" in user_input:
            ai_response = HOPE_CREATOR

        # Crypto, Math, Knowledge
        elif any(op in user_input for op in ["+", "-", "*", "/", "**"]):
            ai_response = f"The answer is: {solve_math(user_input)}"

        elif "crypto price" in user_input or "sol price" in user_input:
            ai_response = get_crypto_prices()

        elif "news" in user_input:
            ai_response = get_trending_news()

        elif "what is" in user_input:
            ai_response = get_general_knowledge(user_input.replace("what is", "").strip())

        else:
            ai_response = run_ollama(user_input)

        print("\nHope:", ai_response, "\n")
        save_memory()  # Save memory after every change

# Start AI chat
chat_with_ai()
