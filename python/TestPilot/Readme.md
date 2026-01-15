# TestPilot - AI Testing & Debugging Agent

TestPilot is a CLI tool that uses AI to analyze your code, identify bugs, and suggest fixes. It supports multiple AI providers: Google Gemini, Zhipu GLM, and OpenRouter (OpenAI).

## Features
- **Multi-Model Support**: Switch between Gemini, GLM, and OpenRouter.
- **Interactive Mode**: Multiline input REPL for quick checks.
- **File Input**: Analyze a whole file using `--file`.
- **Folder Input**: Analyze an entire project folder using `--folder`.
- **Safe Fix Suggestions**: Automatically suggests code fixes for Minor/Info issues (but refuses for Critical/Major ones).

## Setup

1. **Install Dependencies**:
   ```bash
   pip install google-generativeai zhipuai openai
   ```

2. **Configure API Keys**:
   Create a file named `Api.md` in the project directory with your keys:
   ```text
   api key = [YOUR_GEMINI_KEY]
   glm api key = [YOUR_GLM_KEY]
   openrouter api key = [YOUR_OPENROUTER_KEY]
   ```
   (Alternatively, use environment variables: `GEMINI_API_KEY`, `GLM_API_KEY`, `OPENROUTER_API_KEY`)

## Usage

### Interactive Mode
Run without arguments to enter the interactive loop.
```bash
python main.py
```

### Analyze a File
```bash
python main.py --file path/to/script.py
```

### Analyze a Folder
Recursively analyzes all code files in a folder.
```bash
python main.py --folder path/to/project_dir
```

## System Prompt
The AI behavior is controlled by `system_prompt.md`. You can modify this file to change the persona or analysis rules.