import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Path to the users.json file in the same directory
USERS_FILE = Path(__file__).parent / "users.json"

def read_users() -> List[Dict[str, Any]]:
    """Read all users from the JSON file"""
    if not USERS_FILE.exists():
        return []
    
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def write_users(users: List[Dict[str, Any]]) -> None:
    """Write users to the JSON file"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Find a user by their username"""
    users = read_users()
    return next((u for u in users if u["tai_khoan"] == username), None)
def create_user(user: dict) -> None:
    """Add a new user to the database (save to users.json)"""
    users = read_users()
    users.append(user)
    write_users(users)
