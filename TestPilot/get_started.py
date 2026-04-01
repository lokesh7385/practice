import os
import shutil
import re
import tempfile
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
# Connect to TestPilot Engine
import main

app = Flask(__name__)

# Temporary store for analysis results to allow "Apply Fix" lookup by index
# In a real app, this should be a DB or session-based. For local single-user, global is fine.
LATEST_ANALYSIS = {} 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # In cloud mode, files and paths come via form data
    model = request.form.get('model', 'openai')
    files = request.files.getlist('files')
    paths = request.form.getlist('paths')

    if not files or files[0].filename == '':
        return jsonify({"error": "No files uploaded"}), 400

    try:
        keys = main.get_api_keys()
        
        # Create Secure Temp Directory
        session_id = str(uuid.uuid4())
        temp_dir = os.path.join(tempfile.gettempdir(), f"testpilot_{session_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        is_folder = len(files) > 1
        
        # Save files to temp directory
        for i, file_obj in enumerate(files):
            # Paths might include subdirectories (e.g., project/src/main.py)
            rel_path = paths[i] if i < len(paths) else file_obj.filename
            # Sanitize security risk: avoid absolute path traversal
            safe_rel_path = rel_path.lstrip('/').lstrip('\\')
            safe_rel_path = os.path.normpath(safe_rel_path)
            if safe_rel_path.startswith('..'): continue
                
            full_save_path = os.path.join(temp_dir, safe_rel_path)
            os.makedirs(os.path.dirname(full_save_path), exist_ok=True)
            
            file_obj.save(full_save_path)
        
        # Determine the root path to pass to main.py
        # If it's a folder, we pass the root of the temp dir. 
        # If it's a single file, we pass the path to the single file.
        target_path = temp_dir if is_folder else os.path.join(temp_dir, os.path.normpath(paths[0].lstrip('/').lstrip('\\')))
        
        # Run local TestPilot Engine on the temp files
        raw_response = main.analyze_path(target_path, model, keys, is_folder=is_folder)
        
        # Clean up temp files immediately since we are in cloud mode
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        if raw_response.strip().startswith("[") and "ERROR" in raw_response:
             return jsonify({"error": raw_response}), 400
        
        # Parse the structured AI response into JSON
        structured_data = parse_ai_response(raw_response)
        structured_data['path'] = "Uploaded Project/File" # Return friendly name since actual path is a temp UUID
        
        # Store for apply-fix reference (even though apply-fix is disabled in UI, we save it)
        global LATEST_ANALYSIS
        LATEST_ANALYSIS = structured_data
        
        return jsonify(structured_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

@app.route('/apply-fix', methods=['POST'])
def apply_fix():
    return jsonify({"success": False, "error": "Auto-patching is not supported when files are uploaded to the cloud server. Please manually apply the Suggested Fix."}), 400


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
