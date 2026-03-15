"""
app/core/auth.py — Firebase JWT verification middleware
"""
import os
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials

# Asta îi spune lui Swagger să genereze butonul de Authorize
security = HTTPBearer()

def _init_firebase():
    if not firebase_admin._apps:
        # Calea asumată: ești în folderul backend/
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json")
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"CRITIC: Eșec la inițializarea Firebase Admin: {e}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    FastAPI dependency — verifică JWT Firebase.
    Returnează dict cu datele utilizatorului (ex: uid).
    """
    _init_firebase()

    # HTTPBearer se ocupă deja să verifice dacă există "Bearer " în față
    token = credentials.credentials

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")