from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("LOGIN_SECRET_KEY", "change_this_secret_key")  # Set a real secret key in prod

# Add user emails for password reset functionality
USERS = {
    "amar": {
        "password": "mini25",
        "email": "farchoukhamar@gmail.com"
    },
    "ali": {
        "password": "mini15",
        "email": "ali@example.com"
    }
}

# Configure email backend (use real credentials and server in production)
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "admin@example.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "change_this_in_prod")
EMAIL_SMTP_SERVER = os.environ.get("EMAIL_SMTP_SERVER", "smtp.example.com")
EMAIL_SMTP_PORT = int(os.environ.get("EMAIL_SMTP_PORT", 587))

def send_reset_email(recipient_email, username):
    # Compose a simple reset message (in production: use a unique token and a proper HTML template)
    msg = EmailMessage()
    msg["Subject"] = "Internationnella School Password Reset Request"
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient_email
    msg.set_content(
        f"""
Hello {username},

A password reset was requested for your account at Internationnella School.

If you did not request this, you can ignore this email. 
Otherwise, please contact the administrator to finalize your reset (demo).

(This is a demo. In production, include a reset link with a secure token.)

Regards,
Internationnella School Team
""")
    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    user = USERS.get(username)
    if user and user["password"] == password:
        session["username"] = username
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Wrong password, please try again"}), 401

@app.route('/whoami', methods=['GET'])
def whoami():
    if "username" in session:
        return jsonify({"logged_in": True, "username": session["username"]})
    else:
        return jsonify({"logged_in": False})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Hello, {session['username']}! Welcome to the protected area."})

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    identifier = data.get("identifier", "").strip()
    # Allow to enter either username or email
    user = None
    for uname, uinfo in USERS.items():
        if uname == identifier or uinfo.get("email", "").lower() == identifier.lower():
            user = (uname, uinfo)
            break
    # Always respond with generic message for security
    resp_message = "If an account with this email or username exists, a reset link has been sent."
    if user:
        sent = send_reset_email(user[1]["email"], user[0])
        if not sent:
            # Log this in production, but don't reveal to user
            pass
    return jsonify({"success": True, "message": resp_message})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)