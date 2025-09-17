from flask import Flask, request, jsonify
import jwt
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simple user database for testing
users_db = {
    "admin": {
        "username": "admin",
        "password": "password",  # Plain text for testing
        "role": "admin"
    }
}

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.route('/health')
def health():
    logger.info("Health endpoint called")
    return jsonify({"status": "ok"})

@app.route('/login', methods=['POST'])
def login():
    logger.info("Login endpoint called")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request data: {request.data}")
    logger.info(f"Request form: {request.form}")
    logger.info(f"Request json: {request.get_json(silent=True)}")
    try:
        data = request.get_json() or request.form
        logger.info(f"Parsed data: {data}")
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.info("Missing username or password")
            return jsonify({"detail": "Username and password required"}), 400

        user = users_db.get(username)
        if not user or password != user["password"]:
            logger.info("Invalid credentials")
            return jsonify({"detail": "Incorrect username or password"}), 400

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        logger.info("Login successful")
        return jsonify({"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({"detail": "Login failed"}), 500

@app.route('/test')
def test():
    logger.info("Test endpoint called")
    return jsonify({"message": "Test endpoint working"})

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=8000, debug=False)