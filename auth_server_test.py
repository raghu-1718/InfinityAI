#!/usr/bin/env python3
"""
Combined server and test script
"""

import os
import sqlite3
import uuid
import hashlib
import threading
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import uvicorn
import requests

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security config
SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
DB_PATH = "infinityai_auth.db"

# Password hashing
def get_password_hash(password: str) -> str:
    salt = "InfinityAI_Salt_2024"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database functions
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create default admin user
    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "InfinityAI@2024!Secure#Pass")
        hashed_password = get_password_hash(admin_password)

        cursor.execute('''
            INSERT INTO users (id, username, email, hashed_password, full_name, is_active, is_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            "admin",
            "admin@infinityai.pro",
            hashed_password,
            "System Administrator",
            True,
            True
        ))

    conn.commit()
    conn.close()

def get_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, hashed_password, full_name, is_active, is_admin
        FROM users WHERE username = ? AND is_active = 1
    ''', (username,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'hashed_password': result[3],
            'full_name': result[4],
            'is_active': bool(result[5]),
            'is_admin': bool(result[6])
        }
    return None

def create_user_db(username: str, email: str, password: str, full_name: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?",
                  (username, email))
    if cursor.fetchone():
        conn.close()
        return None

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(password)

    cursor.execute('''
        INSERT INTO users (id, username, email, hashed_password, full_name, is_active, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, email, hashed_password, full_name, True, False))

    conn.commit()
    conn.close()
    return user_id

# Auth functions
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User(**user)

# Routes
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register(user_data: UserCreate):
    user_id = create_user_db(
        user_data.username,
        user_data.email,
        user_data.password,
        user_data.full_name
    )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    return {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "message": "User created successfully"
    }

@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "authentication", "database": "sqlite"}

@app.get("/protected")
async def protected(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello, {current_user.username}!",
        "user_id": current_user.id,
        "is_admin": current_user.is_admin
    }

# Initialize database
init_db()

def run_tests():
    """Run tests after server starts"""
    time.sleep(2)  # Wait for server to start

    base_url = "https://www.infinityai.pro"
    print("\n🔍 Testing Authentication Server...")

    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return

    # Test login
    try:
        data = {"username": "admin", "password": "InfinityAI@2024!Secure#Pass"}
        response = requests.post(f"{base_url}/token", data=data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"   Token: {token_data['access_token'][:30]}...")

            # Test protected endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            response = requests.get(f"{base_url}/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print("✅ Protected endpoint access successful!")
                print(f"   User: {user_data['username']}, Admin: {user_data['is_admin']}")
            else:
                print(f"❌ Protected endpoint failed: {response.status_code}")
        else:
            print(f"❌ Login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Login test failed: {e}")

    # Test registration
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        response = requests.post(f"{base_url}/register", json=user_data)
        if response.status_code == 200:
            print("✅ User registration successful!")
        else:
            print(f"❌ Registration failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Registration test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting InfinityAI Authentication Server...")
    print("📊 Default admin credentials:")
    print("   Username: admin")
    print("   Password: InfinityAI@2024!Secure#Pass")
    print("🌐 Server will be available at: https://www.infinityai.pro")
    print("📝 API Documentation: https://www.infinityai.pro/docs")

    # Start test thread
    test_thread = threading.Thread(target=run_tests)
    test_thread.start()

    # Start server
    uvicorn.run(app, host="0.0.0.0", port=8001)
