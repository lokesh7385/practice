import google.generativeai as genai
import os

# Read API key explicitly to match main.py logic
try:
    with open("Api.md", "r") as f:
        for line in f:
            if "api key =" in line.lower():
                key = line.split("=", 1)[1].strip().strip('.')
                genai.configure(api_key=key)
                break
except Exception as e:
    print(f"Error reading key: {e}")

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
