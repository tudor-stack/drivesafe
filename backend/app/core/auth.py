"""
app/core/auth.py — Firebase JWT verification middleware
Persoana 1 implementează asta o singură dată, toate endpoint-urile o folosesc.
"""
import os
from fastapi import HTTPException, Header
from typing import Optional
import firebase_admin
from firebase_admin import auth, credentials


def _init_firebase():
    if not firebase_admin._apps:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI dependency — verifică JWT Firebase din header Authorization: Bearer <token>
    Returnează dict cu uid, email etc.
    """
    _init_firebase()

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split("Bearer ")[1]

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
