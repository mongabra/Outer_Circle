import secrets
import string
import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

# --- Flask App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Needed for session management

# --- Configuration ---
CODE_LENGTH = 4
CODE_CHARS = string.ascii_uppercase + string.digits
DB_FILE = 'user_messages.json' # Renamed to better reflect its content

# --- "Database" Functions ---

def load_messages_db(): #The name of the file used to store all codes and their associated messages.
    """Loads the message database (a dictionary of codes to messages) from a JSON file."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        print(f"Warning: Could not read or parse {DB_FILE}. Starting with an empty database.")
        return {}

def save_messages_db(db):
    """Saves the message database to a JSON file."""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

# --- Core Logic ---

def generate_unique_code(existing_codes): #It runs in a loop to ensure the generated code is unique (not already a key in the existing database).
    """Generates a unique code that is not already in use."""
    while True:
        new_code = ''.join(secrets.choice(CODE_CHARS) for _ in range(CODE_LENGTH))
        if new_code not in existing_codes:
            return new_code

# --- Flask Routes (Web Pages) ---

@app.route('/')
def home():
    """
    Handles the main page. Generates a new code for a new user.
    """
    db = load_messages_db()
    
    # Generate a new, unique code for the user
    user_code = generate_unique_code(db.keys())
    
    # Add the new user to the database with an empty list of messages
    db[user_code] = []
    save_messages_db(db)
    
    # Render the HTML page, passing the new code to it.
    # NOTE: Your HTML file must be in a 'templates' sub-folder.
    return render_template('OuterCircleCode.html', user_code=user_code)

@app.route('/submit-message', methods=['POST'])
def submit_message():
    """
    Handles the form submission.
    """
    db = load_messages_db()
    
    # Get data from the submitted form
    code = request.form.get('user-code')
    message = request.form.get('anon-message')
    sensitivity = request.form.get('sensitivity')
    delivery = request.form.get('delivery')

    # Basic validation
    if not code or code not in db:
        return "Error: Invalid or missing user code.", 400
    if not message:
        return "Error: Message cannot be empty.", 400

    # Create a message object
    new_message = {
        "message": message,
        "sensitivity": sensitivity,
        "delivery": delivery,
        "timestamp_utc": datetime.utcnow().isoformat()
    }
    # Add the message to the user's record and save
    db[code].append(new_message)
    save_messages_db(db)

    # Render the beautiful success page.
    return render_template('success.html')


if __name__ == '__main__':
    # The 'debug=True' part is for development; remove it for production.
    app.run(debug=True)
