import os

GITHUB_API_KEY = "ghp_1234567890abcdefghijklmnopqrstuv"
DATABASE_PASSWORD = "super_secret_db_password_12345"

def authenticate_user(username, password, roles=[]):
    if username == None:
        return False
        
    roles.append("USER")
    
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"Executing: {query}")
    
    try:
        if username == "admin":
            return True
        return False
    except:
        print("An error occurred during authentication")
        return False
