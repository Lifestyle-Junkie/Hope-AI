from flask import Flask, request, jsonify
from flask_cors import CORS  # Enables frontend-backend communication
import subprocess
import json
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# -------------------- Hope AI Logic --------------------

MEMORY_FILE = "hope_memory.json"
HOPE_IDENTITY = "I'm Hope, your AI assistant!"
HOPE_CREATOR = "Nick created me!"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=solana,bitcoin,ethereum&vs_currencies=usd"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php?action=opensearch&search="

# Load memory
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("[ERROR] Corrupted memory file. Resetting...")
    return {}

# Save memory
def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)

# Get crypto prices
def get_crypto_prices():
    try:
        response = requests.get(COINGECKO_API_URL)
        data = response.json()
        return (
            f"Current Prices:\n🔹 SOL: ${data['solana']['usd']}\n"
            f"🔹 BTC: ${data['bitcoin']['usd']}\n🔹 ETH: ${data['ethereum']['usd']}"
        )
    except Exception as e:
        return f"Error fetching prices: {e}"

# Get general knowledge
def get_general_knowledge(query):
    try:
        response = requests.get(f"{WIKIPEDIA_API_URL}{query}&limit=1&namespace=0&format=json")
        data = response.json()
        if data[1]:
            return f"📖 {data[1][0]}: {data[2][0]}\n🔗 {data[3][0]}"
        return "No answer found."
    except Exception as e:
        return f"Error: {e}"

# Solve math expressions
def solve_math(expression):
    try:
        return str(eval(expression))
    except:
        return "I couldn't understand that math problem."

# Default AI fallback
def run_ollama(prompt):
    try:
        result = subprocess.run(["ollama", "run", "llama3", prompt], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"[ERROR] {e}"

# Load memory
memory = load_memory()

# Message processor
def process_input(user_input):
    user_input = user_input.lower().strip()

    if "my" in user_input and "is" in user_input:
        parts = user_input.split(" is ", 1)
        if len(parts) == 2:
            key = parts[0].replace("my", "").strip()
            value = parts[1].strip()
            memory[key] = value
            save_memory()
            return f"Got it! I'll remember that your {key} is {value}."

    elif user_input.startswith("what is my ") or user_input.startswith("what's my "):
        key = user_input.replace("what is my ", "").replace("what's my ", "").strip()
        value = memory.get(key)
        return f"Your {key} is {value}." if value else f"I don't remember your {key}."

    elif user_input.startswith("forget my "):
        key = user_input.replace("forget my ", "").strip()
        if key in memory:
            del memory[key]
            save_memory()
            return f"Okay, I've forgotten your {key}."
        return f"I don't remember your {key}."

    elif "who are you" in user_input or "what is your name" in user_input:
        return HOPE_IDENTITY

    elif "who made you" in user_input or "who created you" in user_input:
        return HOPE_CREATOR

    elif any(op in user_input for op in ["+", "-", "*", "/", "**"]):
        return f"The answer is: {solve_math(user_input)}"

    elif "crypto price" in user_input or "sol price" in user_input:
        return get_crypto_prices()

    elif "what is" in user_input:
        query = user_input.replace("what is", "").strip()
        return get_general_knowledge(query)

    else:
        return run_ollama(user_input)

# -------------------- API Endpoints --------------------

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message", "")
    response = process_input(user_input)
    return jsonify({"reply": response})

# ✅ Add this route to confirm backend is running
@app.route("/")
def home():
    return "Hope AI backend is running!"

# -------------------- Launch App ----------------------

if __name__ == "__main__":
    app.run(debug=True)
