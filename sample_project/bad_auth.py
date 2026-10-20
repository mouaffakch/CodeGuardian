import os

# DEFECT: Hardcoded API Key (SEC001)
GITHUB_API_KEY = "ghp_1234567890abcdefghijklmnopqrstuv"
DATABASE_PASSWORD = "super_secret_db_password_12345"

def authenticate_user(username, password, roles=[]):
    """
    DEFECT: Mutable default argument 'roles=[]' (BUG002)
    """
    # DEFECT: Loose comparison with None (BUG004)
    if username == None:
        return False
        
    roles.append("USER")
    
    # DEFECT: SQL Injection via f-string (SEC002)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"Executing: {query}")
    
    try:
        # Mock database execution
        if username == "admin":
            return True
        return False
    except:
        # DEFECT: Bare except clause (BUG001)
        print("An error occurred during authentication")
        return False

# Hotfix commit test

