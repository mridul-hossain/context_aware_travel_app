import requests
from google_auth_oauthlib.flow import InstalledAppFlow
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "travel_companion.db"
CLIENT_SECRET_PATH = Path(__file__).parent / "assets" / "client_secret.json"

# Scopes define what data we want from Google
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

def google_login_flow():
    """
    Opens browser for Google Login, gets token, fetches user info,
    saves to SQLite, and returns user dict.
    """
    try:
        # 1. Run the OAuth Flow
        # Note: This requires 'client_secret.json' in your folder
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_PATH.as_posix(), SCOPES)
        
        # This opens a local browser window for the user to sign in
        creds = flow.run_local_server(port=0)

        # 2. Fetch User Info using the credentials
        if creds and creds.valid:
            session = requests.Session()
            session.headers.update({'Authorization': f'Bearer {creds.token}'})
            user_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
            
            # 3. Save/Update User in SQLite
            save_user_to_db(user_info)
            
            return user_info
    except Exception as e:
        print(f"Login Failed: {e}")
        return None

def save_user_to_db(user_data):
    conn = sqlite3.connect(DB_PATH.as_posix())
    c = conn.cursor()
    
    # Insert or Ignore (if user exists)
    email = user_data.get('email')
    name = user_data.get('name')
    picture = user_data.get('picture')

    # Check if user exists
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    exists = c.fetchone()

    if not exists:
        c.execute("INSERT INTO users (email, name, profile_pic) VALUES (?, ?, ?)", 
                  (email, name, picture))
    else:
        # Update info just in case
        c.execute("UPDATE users SET name=?, profile_pic=? WHERE email=?", 
                  (name, picture, email))

    conn.commit()
    conn.close()