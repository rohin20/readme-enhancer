from flask import Flask, render_template, request, send_file, url_for, session
import os
import re
import jinja2
import random
import requests
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.secret_key = "emoji_readme_secret_key"  # Required for session
UPLOAD_FOLDER = "uploads"
UPDATED_FOLDER = "updated"
STATIC_FOLDER = "static"

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPDATED_FOLDER, exist_ok=True)
os.makedirs(os.path.join(app.root_path, STATIC_FOLDER), exist_ok=True)

def setup_github_logo():
    """Ensure the GitHub logo exists in the static folder"""
    logo_path = os.path.join(app.root_path, STATIC_FOLDER, "github-logo.png")
    
    # Only create if it doesn't exist
    if not os.path.exists(logo_path):
        try:
            # Create a simple purple circle (200x200 pixels)
            img = Image.new('RGB', (200, 200), (102, 51, 153))  # Purple color
            
            # Save the image
            img.save(logo_path, 'PNG')
            print(f"Created GitHub logo at {logo_path}")
        except Exception as e:
            print(f"Error creating GitHub logo: {e}")

# Call this function during app initialization
setup_github_logo()

# Configure Jinja2 to not auto-escape in JS blocks
app.jinja_env.autoescape = False

# Simple keyword-to-emoji mapping
EMOJI_MAP = {
    "important": "🔥",
    "note": "📝",
    "warning": "⚠️",
    "check": "✅",
    "info": "ℹ️",
    "success": "🎉",
    "error": "❌",
    "tip": "💡"
}

# Default header and list emoji maps
DEFAULT_HEADER_EMOJI_MAP = {
    "#": "📌",    # H1
    "##": "🔹",   # H2
    "###": "⚡",  # H3
}

DEFAULT_LIST_EMOJI_MAP = {
    "-": "✅",
    "+": "✅",
    "*": "✅",
}

# Available emoji options for user selection
HEADER_EMOJI_OPTIONS = {
    "h1": ["📌", "🚀", "🌟", "💫", "🔮", "🏆", "💎", "🎯"],
    "h2": ["🔹", "✨", "🌈", "🔍", "🌱", "📊", "🧩", "📱"],
    "h3": ["⚡", "🔆", "📎", "🔧", "📚", "🧠", "🛠️", "🔗"]
}

LIST_EMOJI_OPTIONS = ["✅", "🔸", "🔹", "▪️", "•", "👉", "🔘", "📍"]

def add_emojis_to_readme(content, header_emoji_map, list_emoji_map):
    # Add emojis based on keyword mapping
    for word, emoji in EMOJI_MAP.items():
        content = content.replace(word, f"{emoji} {word}")
    
    # Add emojis to headers (H1, H2, H3)
    def replace_headers(match):
        prefix = match.group(1)
        title = match.group(2)
        
        # Select random emoji from appropriate list
        emoji_list = header_emoji_map.get(prefix, ["✨"])
        emoji = random.choice(emoji_list) if emoji_list else "✨" # Fallback
            
        return f"{prefix} {emoji} {title}"
    
    content = re.sub(r"^(#{1,3})\s*(.*)$", replace_headers, content, flags=re.MULTILINE)
    
    # Add emojis to list items
    def replace_list_items(match):
        prefix = match.group(1)
        text = match.group(2)
        
        # Select random emoji from list emoji list
        emoji_list = list_emoji_map.get("list", ["✅"])
        emoji = random.choice(emoji_list) if emoji_list else "✅" # Fallback
            
        return f"{prefix} {emoji} {text}"
    
    content = re.sub(r"^(\s*[-+*])\s+(.*)$", replace_list_items, content, flags=re.MULTILINE)
    
    return content

def escape_for_js(text):
    """Escape text to be included in JavaScript string literals"""
    return text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

def parse_custom_emojis(text):
    """Parse custom emojis from text input"""
    if not text or not text.strip():
        return []
    
    # Split by commas or spaces
    emojis = re.split(r'[, ]+', text.strip())
    return [e for e in emojis if e]  # Remove empty strings

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Check if this is a file upload or emoji selection form
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename.endswith(".md"):
                original_content = file.read().decode("utf-8")
                
                # Save the original content
                original_path = os.path.join(UPLOAD_FOLDER, "original_readme.md")
                with open(original_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
                
                # Store in session for later use
                session["original_content"] = original_content
                
                # Render the emoji selection page
                return render_template(
                    "emoji_options.html",
                    h1_options=HEADER_EMOJI_OPTIONS["h1"],
                    h2_options=HEADER_EMOJI_OPTIONS["h2"],
                    h3_options=HEADER_EMOJI_OPTIONS["h3"],
                    list_options=LIST_EMOJI_OPTIONS
                )
        
        # If it's the emoji selection form
        elif "apply_emojis" in request.form:
            original_content = session.get("original_content", "")
            if not original_content:
                return render_template("upload.html", error="Session expired. Please upload your file again.")
            
            # Get user selections for each category
            h1_emojis = request.form.getlist("h1_emoji")
            h2_emojis = request.form.getlist("h2_emoji")
            h3_emojis = request.form.getlist("h3_emoji")
            list_emojis = request.form.getlist("list_emoji")
            
            # Add custom emojis if provided
            h1_emojis.extend(parse_custom_emojis(request.form.get("custom_h1_emoji", "")))
            h2_emojis.extend(parse_custom_emojis(request.form.get("custom_h2_emoji", "")))
            h3_emojis.extend(parse_custom_emojis(request.form.get("custom_h3_emoji", "")))
            list_emojis.extend(parse_custom_emojis(request.form.get("custom_list_emoji", "")))
            
            # Use default emojis if none selected
            if not h1_emojis:
                h1_emojis = [DEFAULT_HEADER_EMOJI_MAP["#"]]
            if not h2_emojis:
                h2_emojis = [DEFAULT_HEADER_EMOJI_MAP["##"]]
            if not h3_emojis:
                h3_emojis = [DEFAULT_HEADER_EMOJI_MAP["###"]]
            if not list_emojis:
                list_emojis = [DEFAULT_LIST_EMOJI_MAP["-"]]
            
            # Create emoji map
            emoji_map = {
                "#": h1_emojis,
                "##": h2_emojis,
                "###": h3_emojis,
            }
            
            list_emoji_map = {
                "list": list_emojis
            }
            
            # Generate and save the updated content
            updated_content = add_emojis_to_readme(
                original_content, 
                emoji_map,
                list_emoji_map
            )
            
            updated_path = os.path.join(UPDATED_FOLDER, "updated_readme.md")
            with open(updated_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            # Escape content for JavaScript
            escaped_original = escape_for_js(original_content)
            escaped_updated = escape_for_js(updated_content)
            
            return render_template(
                "display.html", 
                original_content=escaped_original,
                updated_content=escaped_updated
            )
            
    return render_template("upload.html")

@app.route("/download")
def download_file():
    updated_path = os.path.join(UPDATED_FOLDER, "updated_readme.md")
    return send_file(updated_path, as_attachment=True)

@app.route("/how-to-use")
def how_to_use():
    return render_template("how_to_use.html")

if __name__ == "__main__":
    app.run(debug=True)