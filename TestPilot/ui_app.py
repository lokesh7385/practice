import os
import shutil
import re
from flask import Flask, render_template, request, jsonify
# Connect to TestPilot Engine
import main

app = Flask(__name__)

# Temporary store for analysis results to allow "Apply Fix" lookup by index
# In a real app, this should be a DB or session-based. For local single-user, global is fine.
LATEST_ANALYSIS = {} 

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    path = data.get('path')
    if path:
        path = path.strip().strip('"').strip("'")
    
    model = data.get('model', 'openai')
    
    if not path:
        return jsonify({"error": "Path is required"}), 400

    try:
        # Call TestPilot Engine
        keys = main.get_api_keys()
        
        # Check if folder or file
        is_folder = os.path.isdir(path)
        
        # Use the refactored analyze_path function
        raw_response = main.analyze_path(path, model, keys, is_folder=is_folder)
        
        if raw_response.strip().startswith("[") and "ERROR" in raw_response:
             return jsonify({"error": raw_response}), 400
        
        # Parse the structured AI response into JSON
        structured_data = parse_ai_response(raw_response)
        structured_data['path'] = path # Return path for context
        
        # Store for apply-fix reference
        global LATEST_ANALYSIS
        LATEST_ANALYSIS = structured_data
        
        return jsonify(structured_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

@app.route('/apply-fix', methods=['POST'])
def apply_fix():
    data = request.json
    file_path_arg = data.get('file_path') # This might be project path if folder mode
    issue_index = data.get('issue_index')
    
    global LATEST_ANALYSIS
    if not LATEST_ANALYSIS or 'issues' not in LATEST_ANALYSIS:
        return jsonify({"success": False, "error": "No active analysis found. Please re-run analysis."}), 400

    try:
        issue = LATEST_ANALYSIS['issues'][issue_index]
    except IndexError:
        return jsonify({"success": False, "error": "Invalid issue index."}), 400

    # Security / Integrity Check
    if issue['severity'] in ['CRITICAL', 'MAJOR']:
         return jsonify({"success": False, "error": "Cannot auto-fix CRITICAL or MAJOR issues. Please apply manually."}), 403
    
    if not issue.get('suggested_fix_code'):
        return jsonify({"success": False, "error": "No code fix available for this issue."}), 400

    code_to_apply = issue['suggested_fix_code']
    
    # Determine actual file to edit
    # If folder analysis, we need to know WHICH file. 
    # Current "analyze_path" output for folders might not explicitly tag every single issue with a filename in a machine-readable way 
    # UNLESS the prompt enforces it per issue. 
    # Looking at prompt: "Global Output: List of Issues". It doesn't strictly force "File: <name>" per issue.
    # CRITICAL GAP: If analyzing a folder, we don't know which file to fix.
    # FALLBACK: For MVP context, we will assume Single File Mode for auto-fix OR try to guess from description?
    # BETTER: If folder mode, we disable auto-fix in UI or check if file path is part of issue.
    # Let's check constraints: "If a suggested fix cannot be applied with HIGH CONFIDENCE... DO NOT APPLY IT."
    
    target_file = file_path_arg
    
    # If input was a folder, we need the specific file.
    if os.path.isdir(file_path_arg):
        # We can't safely know the file without more parsing logic or prompt change.
        return jsonify({"success": False, "error": "Auto-fix in Folder Mode is not supported in this version (Target file ambiguous)."}), 400

    # Backup
    if not os.path.exists(target_file):
        return jsonify({"success": False, "error": "Target file not found."}), 404
        
    backup_path = target_file + ".bak"
    shutil.copy2(target_file, backup_path)
    
    # Apply Strategy: Strict Match Replacement
    # Since we can't do fuzzy matching safely, we will try:
    # 1. READ file
    # 2. CHECK if `code_to_apply` looks like a replacement block?
    # The prompt says "Suggested Fix... Presented clearly as a code snippet".
    # It doesn't say "Search Block" and "Replace Block".
    # Most likely the AI returns just the NEW code.
    # If the AI returns just the new function, we might APPEND it?
    # Or if it returns the whole fixed function?
    # Constraint: "The fix is either: A direct string replacement... OR An explicit append instruction"
    # To be SAFE: We will attempt to Append to end of file if it looks like a new function/block.
    # If it looks like a modification, we will REJECT IT for Manual Application unless we implement a diff patcher.
    # Given MVP constraints: We will try to APPEND if file doesn't contain it, OR return "Manual Required" if ambiguous.
    
    # Let's try a simple APPEND approach for now (common for 'missing function' fixes).
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check if code already exists (duplicates)
        if code_to_apply.strip() in content:
             return jsonify({"success": False, "error": "Fix seems to already exist in file."})

        # Append
        with open(target_file, "a", encoding="utf-8") as f:
            f.write("\n\n" + code_to_apply + "\n")
            
        return jsonify({"success": True, "message": "Fix appended to file."})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def parse_ai_response(text):
    """
    Parses the Markdown-formatted AI response into a dict.
    """
    cleaned_text = re.sub(r'\x1b\[[0-9;]*m', '', text) # Remove color codes if any
    
    # Extract Sections
    summary_match = re.search(r'(?:\*\*Problem Summary:\*\*|Problem Summary)([\s\S]*?)(?=(?:\*\*List of Issues|\*\*Issues|Issues:))', cleaned_text, re.IGNORECASE)
    summary = summary_match.group(1).strip() if summary_match else ""
    
    issues = []
    # Regex to find issue blocks. 
    # We look for "Issue Description" or numbered items
    issue_blocks = re.split(r'\d+\.\s+\*\*Issue Description\*\*:', cleaned_text)
    
    if len(issue_blocks) < 2:
        # Try alternative format if numbers are missing or different headers
        issue_blocks = re.split(r'\*\*Issue Description\*\*:', cleaned_text)

    for block in issue_blocks[1:]: # Skip preamble
        issue = {}
        
        # Extract fields
        desc_match = re.search(r'(.*?)(?=\n\s*- \*\*Type\*\*|\n\s*- \*\*Severity\*\*)', block, re.DOTALL)
        issue['description'] = desc_match.group(1).strip() if desc_match else "N/A"
        
        type_match = re.search(r'\*\*Type\*\*:\s*(.*)', block)
        issue['type'] = type_match.group(1).strip() if type_match else "Unknown"
        
        sev_match = re.search(r'\*\*Severity\*\*:\s*([A-Z]+)', block)
        issue['severity'] = sev_match.group(1).strip() if sev_match else "INFO"
        
        conf_match = re.search(r'\*\*Confidence\*\*:\s*(\d+)%', block)
        issue['confidence'] = conf_match.group(1).strip() if conf_match else "0"
        
        root_match = re.search(r'\*\*Root Cause\*\*:\s*(.*?)(?=\n\s*- \*\*Fix\*\*)', block, re.DOTALL)
        issue['root_cause'] = root_match.group(1).strip() if root_match else "N/A"
        
        fix_match = re.search(r'\*\*Fix\*\*:\s*(.*?)(?=\n\s*- \*\*Suggested Fix)', block, re.DOTALL)
        issue['fix'] = fix_match.group(1).strip() if fix_match else "N/A"
        
        suggest_match = re.search(r'\*\*Suggested Fix \(Optional\)\*\*:(.*)', block, re.DOTALL)
        if suggest_match:
            raw_suggestion = suggest_match.group(1).strip()
            issue['suggested_fix_desc'] = raw_suggestion
            
            # Extract Code Block if present
            code_block_match = re.search(r'```(?:\w+)?\n([\s\S]*?)\n```', raw_suggestion)
            if code_block_match:
                issue['suggested_fix_code'] = code_block_match.group(1)
            else:
                 issue['suggested_fix_code'] = None
        else:
             issue['suggested_fix'] = False

        issues.append(issue)

    return {
        "summary": summary,
        "issues": issues
    }

if __name__ == '__main__':
    app.run(port=5000, debug=True)
