import os
import json
import requests
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from urllib.parse import urlencode
import time


load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BLOGGER_SCOPES = os.getenv("BLOGGER_SCOPES", "https://www.googleapis.com/auth/blogger") # Default scope if not set
REDIRECT_URI = "http://localhost:8000/callback" # Must match your Google Cloud Console setting

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
TOKEN_FILE = "blogger_token.json"


app = FastAPI()

# --- Helper Functions ---

def generate_auth_url():
    """Generates the Google OAuth authorization URL."""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": BLOGGER_SCOPES,
        "response_type": "code",
        "access_type": "offline",  # Important: requests offline access to get a refresh token
    }
    return f"{AUTH_URI}?{urlencode(params)}"

def get_access_token(code: str):
    """Exchanges the authorization code for access and refresh tokens."""
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(TOKEN_URI, data=token_data)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        if response:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")
        return None

def save_token_data(token_info: dict):
    """Saves the token data to blogger_token.json."""
    try:
        # Ensure refresh_token is present
        if 'refresh_token' not in token_info:
            print("🚨 WARNING: Refresh token not found in the response. Future token refreshes will fail.")
            print("   Make sure 'access_type=offline' is in the auth URL.")
            
        # Ensure a basic structure for compatibility with the original script
        formatted_data = {
            "access_token": token_info.get("access_token"),
            "refresh_token": token_info.get("refresh_token"),
            "token_type": token_info.get("token_type", "Bearer"),
            "expires_in": token_info.get("expires_in"),
            # Adding expiration timestamp for easier check in other apps
            "issued_at": int(time.time()), 
            "expires_at": int(time.time()) + token_info.get("expires_in", 0)
        }

        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Token data saved successfully to {TOKEN_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error saving token data: {e}")
        return False

def read_token_data():
    """Reads token data from blogger_token.json."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error reading {TOKEN_FILE}: {e}")
            return None
    return None

# --- API Routes ---

@app.get("/")
async def homepage():
    """Homepage to initiate the OAuth flow."""
    if not CLIENT_ID or not CLIENT_SECRET:
        return {"error": "Google Client ID or Secret not configured in .env file."}

    # Check if token already exists and is valid
    token_info = read_token_data()
    if token_info:
        now = int(time.time())
        if token_info.get("access_token") and token_info.get("expires_at", 0) > now + 300: # Check if token is still somewhat valid (e.g., > 5 mins life)
             return {"message": "Existing token found. Token is still valid.", "token_details": token_info}
        elif token_info.get("refresh_token"):
             print("Existing refresh token found, but access token is expired or missing. Please re-authenticate.")
        else:
             print("Existing token file found, but it's incomplete or expired. Please re-authenticate.")

    auth_url = generate_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(code: str | None = None, error: str | None = None):
    """Callback endpoint to receive the authorization code from Google."""
    if error:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth Error: {error}"
        )
    
    if not code:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not received."
        )
        
    print(f"Received authorization code: {code[:10]}...") # Print first 10 chars for brevity
    
    token_info = get_access_token(code)
    
    if token_info:
        if save_token_data(token_info):
            return {
                "message": "Successfully obtained and saved tokens!",
                "token_details": token_info,
                "file_created": TOKEN_FILE
            }
        else:
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save token data."
            )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to exchange authorization code for tokens. Check server logs."
        )

@app.get("/get_token")
async def get_token():
    """Endpoint to read the current token data from the file."""
    token_info = read_token_data()
    if token_info:
        return token_info
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{TOKEN_FILE} not found or could not be read. Please run the OAuth flow first."
        )

# --- How to Run ---
# 1. Save this code as `main.py`
# 2. Create a `.env` file with your GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, etc.
# 3. Run the server: `uvicorn main:app --reload --port 8000`
# 4. Open your browser to: `http://localhost:8000/`
# 5. Follow the prompts to authorize the application.
# 6. After authorization, `blogger_token.json` will be created in the same directory.

if __name__ == "__main__":
    import uvicorn
    # Check for essential environment variables before starting
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file.")
    else:
        uvicorn.run(app, host="localhost", port=8000)