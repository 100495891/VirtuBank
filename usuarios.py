import json, hashlib, os
USERS_FILE = 'usuarios.json'
def crear_contraseña(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE,'r') as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USERS_FILE,'w') as file:
        json.dump(users, file, indent=4)

def register_user(username, password):
    users = load_users()
    if username in users:
        raise ValueError("User already exists")
    users[username] = crear_contraseña(password)
    save_users(users)
    print(f"User {username} registered successfully")

def authenticate_user(username, password):
    users = load_users()
    if username not in users:
        return False
    return users[username] == crear_contraseña(password)