from dotenv import load_dotenv
load_dotenv()  # Loads local .env (ignored on Railway but safe)

import os
import secrets
import string
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

import database as db  # Your database module

# ---- Configuration ----
CODE_LENGTH = 4
CODE_CHARS = string.ascii_uppercase + string.digits


def generate_unique_code():
    """Generates a 4-character unique code and ensures it's not already in the DB."""
    while True:
        code = ''.join(secrets.choice(CODE_CHARS) for _ in range(CODE_LENGTH))
        if not db.code_exists(code):
            return code


# ----------------------------------------------------------------
#  FLASK APPLICATION FACTORY — REQUIRED FOR RAILWAY + GUNICORN
# ----------------------------------------------------------------
def create_app():
    app = Flask(__name__)

    # Attach DB functions + teardown to the app
    db.init_app(app)

    # ----------------- ROUTES -----------------

    @app.route('/')
    def home():
        error_message = request.args.get('error')
        return render_template('start.html', error=error_message)

    @app.route('/new-code')
    def new_code():
        code = generate_unique_code()
        db.create_user(code)
        return render_template('OuterCircleCode.html', code=code)

    @app.route('/submit/<string:code>')
    def show_submit_page(code):
        if db.code_exists(code):
            return render_template('OuterCircleCode.html', code=code)
        return redirect(url_for('home', error="Invalid code. Please try again or get a new one."))

    @app.route('/login', methods=['POST'])
    def login():
        code = request.form.get('user-code', '').upper()
        if code and db.code_exists(code):
            return redirect(url_for('show_submit_page', code=code))
        return render_template('start.html', error="Invalid code. Please try again or get a new one.")

    @app.route('/submit-message', methods=['POST'])
    def submit_message():
        code = request.form.get('user-code', '').upper()
        message_text = request.form.get('anon-message')
        sensitivity = request.form.get('sensitivity')
        delivery = request.form.get('delivery')

        if not code or not db.code_exists(code):
            return render_template('Error.html'), 400
        if not message_text:
            return "Error: Message cannot be empty.", 400

        new_message = {
            "message": message_text,
            "sensitivity": sensitivity,
            "delivery": delivery,
            "timestamp_utc": datetime.utcnow().isoformat()
        }

        db.add_message_for_code(code, new_message)
        return render_template('EncouragementPage.html', code=code)

    @app.route('/messages')
    def view_messages():
        all_messages = db.get_all_messages_grouped()
        return render_template('admin_view.html', messages=all_messages)

    return app


# -----------------------------------------------------
#  LOCAL DEVELOPMENT ENTRY POINT
# -----------------------------------------------------
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
