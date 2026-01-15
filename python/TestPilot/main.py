import os
import sys
import argparse
import io

# Ensure UTF-8 output for Windows terminals
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Configuration ---
DEFAULT_SYSTEM_PROMPT = """
You are a software testing and debugging assistant.

Analyze the given input and identify bugs, runtime errors, or bad practices.
Provide a clear summary, root cause, and minimal fix.

If the input is unclear, state assumptions.
"""

# Try importing Google Generative AI
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Try importing ZhipuAI
try:
    from zhipuai import ZhipuAI
    HAS_GLM = True
except ImportError:
    HAS_GLM = False

# Try importing OpenAI
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# --- Helper Functions ---

def get_system_prompt():
    """Reads the system prompt from system_prompt.md or returns default."""
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.md")
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"[WARN] Failed to read system_prompt.md: {e}")
    return DEFAULT_SYSTEM_PROMPT

def get_multiline_input():
    """Reads multiline input from the user until specific terminator is found."""
    print("Enter your code/error below. Type 'DONE' on a new line to submit, or 'EXIT' to quit.")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "DONE":
            break
        if line.strip() == "EXIT":
            return None
        lines.append(line)
    return "\n".join(lines)

def get_api_keys():
    """
    Retrieves API keys from environment or Api.md file.
    Returns a dict: {'gemini': key, 'glm': key, 'openai': key}
    """
    keys = {
        'gemini': os.getenv("GEMINI_API_KEY"),
        'glm': os.getenv("GLM_API_KEY"),
        'openai': os.getenv("OPENAI_API_KEY")
    }
    
    api_file_path = os.path.join(os.path.dirname(__file__), "Api.md")
    if os.path.exists(api_file_path):
        try:
            with open(api_file_path, "r") as f:
                for line in f:
                    lower_line = line.lower().strip()
                    if lower_line.startswith("api key") and not lower_line.startswith("glm") and not lower_line.startswith("openai"):
                        # Gemini
                        parts = line.split("=", 1)
                        if len(parts) > 1:
                            keys['gemini'] = parts[1].strip()
                    elif lower_line.startswith("glm api key"):
                        parts = line.split("=", 1)
                        if len(parts) > 1:
                            keys['glm'] = parts[1].strip()
                    elif lower_line.startswith("openai api key"):
                        parts = line.split("=", 1)
                        if len(parts) > 1:
                            keys['openai'] = parts[1].strip()
        except Exception as e:
            print(f"[WARN] Failed to read Api.md: {e}")
            
    return keys

def analyze_with_gemini(user_input, api_key):
    if not HAS_GENAI:
        return "[ERROR] `google-generativeai` library not found."
    
    try:
        genai.configure(api_key=api_key)
        # Using a model known to be widely available or the one we verified earlier
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        system_prompt = get_system_prompt()
        full_prompt = f"{system_prompt}\n\nUSER INPUT:\n{user_input}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"[GEMINI API ERROR] {e}"

def analyze_with_glm(user_input, api_key):
    if not HAS_GLM:
        return "[ERROR] `zhipuai` library not found. Please run: pip install zhipuai"
    
    try:
        client = ZhipuAI(api_key=api_key) 
        system_prompt = get_system_prompt()
        
        response = client.chat.completions.create(
            model="glm-4", # Standard model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GLM API ERROR] {e}"

def analyze_with_openrouter(user_input, api_key):
    if not HAS_OPENAI:
        return "[ERROR] `openai` library not found. Please run: pip install openai"
    
    try:
        # OpenRouter uses the OpenAI client but with a specific base URL
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        system_prompt = get_system_prompt()
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-v3.2", # OpenRouter requires vendor prefix usually, or maps standard names
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            extra_headers={
                "HTTP-Referer": "https://github.com/TestPilot/MVP", # Required/Recommended by OpenRouter
                "X-Title": "TestPilot MVP",
            },
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[OPENROUTER API ERROR] {e}"


# --- Main CLI ---

def analyze_path(path_arg, model_name, api_keys, is_folder=False):
    """
    Analyzes a file or folder path using the specified model.
    Returns the AI response string.
    """
    if has_glm := api_keys.get('glm'): pass # ensure imports don't flag unused if only this function used
    
    # 1. Gather Content
    full_content = []
    
    if is_folder:
        if not os.path.exists(path_arg) or not os.path.isdir(path_arg):
             return f"[ERROR] Folder not found or invalid: {path_arg}"
        
        project_name = os.path.basename(os.path.abspath(path_arg))
        valid_extensions = {".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".ts", ".json"}
        
        try:
            for root, dirs, files in os.walk(path_arg):
                dirs[:] = [d for d in dirs if not d.startswith('.')] # Skip hidden
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext.lower() not in valid_extensions:
                        continue
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path_arg)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            full_content.append(f"PROJECT: {project_name}\nFILE: {rel_path}\n{content}\n")
                    except Exception as e:
                        print(f"[WARN] Skipped file {rel_path}: {e}")
            
            if not full_content:
                return "[WARN] No valid code files found in the folder."
            
            final_input = "\n".join(full_content)
            
        except Exception as e:
             return f"[ERROR] Failed to read folder: {e}"

    else: # File mode
        if not os.path.exists(path_arg):
            return f"[ERROR] File not found: {path_arg}"
        try:
            with open(path_arg, "r", encoding="utf-8") as f:
                content = f.read()
            filename = os.path.basename(path_arg)
            _, ext = os.path.splitext(filename)
            file_type = ext.lstrip('.') if ext else "unknown"
            final_input = f"FILE NAME: {filename}\nFILE TYPE: {file_type}\nFILE CONTENT:\n{content}"
        except Exception as e:
            return f"[ERROR] Could not read file: {e}"

    # 2. Call AI
    print(f"\nAnalyzing (via {model_name.upper()})...\n")
    if model_name == "gemini":
        return analyze_with_gemini(final_input, api_keys['gemini'])
    elif model_name == "glm":
        return analyze_with_glm(final_input, api_keys['glm'])
    else:
        return analyze_with_openrouter(final_input, api_keys['openai'])


def main():
    parser = argparse.ArgumentParser(description="TestPilot - AI Software Testing & Debugging Agent")
    parser.add_argument("--file", "-f", help="Path to the file to analyze")
    parser.add_argument("--folder", help="Path to the folder to analyze")
    args = parser.parse_args()

    print("Welcome to TestPilot - AI Testing & Debugging Agent")
    print("---------------------------------------------------")
    
    keys = get_api_keys()
    
    # Selection Menu
    available_options = []
    if keys.get('gemini'):
        available_options.append(("Gemini", "1"))
    if keys.get('glm'):
        available_options.append(("GLM (ZhipuAI)", "2"))
    if keys.get('openai'):
        available_options.append(("OpenRouter", "3"))
        
    if not available_options:
        print("[ERROR] No API keys found in Api.md or environment.")
        print("Please check your Api.md file.")
        return

    print("Select AI Model:")
    for name, code in available_options:
        print(f"[{code}] {name}")
    
    selected_model_code = None
    selected_model_name = None
    
    while not selected_model_code:
        choice = input("Choice: ").strip()
        if choice == "1" and keys.get('gemini'):
             selected_model_name = "gemini"
             selected_model_code = "1"
        elif choice == "2" and keys.get('glm'):
             selected_model_name = "glm"
             selected_model_code = "2"
        elif choice == "3" and keys.get('openai'):
             selected_model_name = "openrouter"
             selected_model_code = "3"
        else:
             print("Invalid choice. Try again.")

    print(f"\nUsing {selected_model_name.upper()}...")

    # Folder Mode
    if args.folder:
        response = analyze_path(args.folder, selected_model_name, keys, is_folder=True)
        print("--- AI Response ---")
        try:
            print(response)
        except UnicodeEncodeError:
            print(response.encode('utf-8', errors='ignore').decode('utf-8'))
        print("-------------------\n")
        return

    # File Mode
    if args.file:
        response = analyze_path(args.file, selected_model_name, keys, is_folder=False)
        print("--- AI Response ---")
        try:
            print(response)
        except UnicodeEncodeError:
            print(response.encode('utf-8', errors='ignore').decode('utf-8'))
        print("-------------------\n")
        return

    # Interactive Mode
    while True:
        user_input = get_multiline_input()
        if user_input is None:
            print("Exiting...")
            break
        
        if not user_input.strip():
            continue

        # For interactive mode, we just pass the text directly. 
        # But analyze_path expects a path. We can just use the underlying functions directly or strip that logic out? 
        # The prompt asked to extract "core logic" into a callable function implementation.
        # Let's just call the underlying analyze_with_X directly for interactive mode to avoid complexity,
        # OR format it as a "text content" if we wanted to reuse analyze_path, but analyze_path takes a path.
        # So sticking to direct calls for interactive mode is cleaner.
        
        print(f"\nAnalyzing (via {selected_model_name.upper()})...\n")
        if selected_model_name == "gemini":
            response = analyze_with_gemini(user_input, keys['gemini'])
        elif selected_model_name == "glm":
            response = analyze_with_glm(user_input, keys['glm'])
        else:
            response = analyze_with_openrouter(user_input, keys['openai'])
            
        print("--- AI Response ---")
        try:
            print(response)
        except UnicodeEncodeError:
             print(response.encode('utf-8', errors='ignore').decode('utf-8'))
        print("-------------------\n")

if __name__ == "__main__":
    main()
