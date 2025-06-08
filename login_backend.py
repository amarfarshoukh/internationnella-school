from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("LOGIN_SECRET_KEY", "change_this_secret_key")  # Set a real secret key in prod

USERS = {
    "amar": "mini25",
    "ali": "mini15"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    # Basic check, replace with DB query in production
    if username in USERS and USERS[username] == password:
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

# To protect other endpoints, you can use a decorator
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Example of a protected route
@app.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Hello, {session['username']}! Welcome to the protected area."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)