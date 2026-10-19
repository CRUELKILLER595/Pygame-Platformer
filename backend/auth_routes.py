
import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from firebase_admin import firestore

from firebase_client import db


# Load environment variables from the backend's .env file.
load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

FIREBASE_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "").strip().strip('"')
FIREBASE_AUTH_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts"
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class SignupRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


# --------------------------------------------------
# FIREBASE AUTHENTICATION HELPER
# --------------------------------------------------

def firebase_auth(action: str, payload: dict) -> dict:
    """Send an email/password authentication request to Firebase."""

    if not FIREBASE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="FIREBASE_WEB_API_KEY is not configured in .env.",
        )

    url = f"{FIREBASE_AUTH_URL}:{action}"

    try:
        response = requests.post(
            url,
            params={"key": FIREBASE_API_KEY},
            json=payload,
            timeout=15,
        )
    except requests.RequestException as exc:
        print("Firebase connection error:", repr(exc))
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Firebase Authentication.",
        ) from exc

    try:
        result = response.json()
    except ValueError as exc:
        print(
            "Firebase returned a non-JSON response:",
            response.status_code,
            response.text[:300],
        )
        raise HTTPException(
            status_code=502,
            detail="Firebase returned an unexpected response.",
        ) from exc

    # Firebase accepted the request.
    if response.ok:
        return result

    # Firebase rejected the request. Identify its error.
    error = result.get("error") or {}
    error_code = error.get("message", "UNKNOWN_ERROR")

    # Log the error code only; never log passwords or tokens.
    print("Firebase authentication error:", error_code)

    if error_code == "EMAIL_EXISTS":
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    if error_code in {
        "INVALID_LOGIN_CREDENTIALS",
        "EMAIL_NOT_FOUND",
        "INVALID_PASSWORD",
        "USER_DISABLED",
    }:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password, or account unavailable.",
        )

    if error_code == "INVALID_EMAIL":
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid email address.",
        )

    if error_code.startswith("WEAK_PASSWORD"):
        raise HTTPException(
            status_code=400,
            detail="Password does not meet Firebase requirements.",
        )

    if error_code == "OPERATION_NOT_ALLOWED":
        raise HTTPException(
            status_code=400,
            detail="Enable Email/Password in Firebase Authentication settings.",
        )

    if error_code in {"API_KEY_INVALID", "INVALID_API_KEY"}:
        raise HTTPException(
            status_code=503,
            detail="Firebase Web API key is invalid.",
        )

    raise HTTPException(
        status_code=400,
        detail=f"Firebase authentication failed: {error_code}",
    )


# --------------------------------------------------
# SIGN UP
# --------------------------------------------------

@router.post("/signup", status_code=201)
def signup(body: SignupRequest):
    display_name = body.display_name.strip()
    email = body.email.strip().lower()

    if not display_name:
        raise HTTPException(
            status_code=400,
            detail="Display name cannot be empty.",
        )

    # Create the account using Firebase Authentication.
    auth = firebase_auth(
        "signUp",
        {
            "email": email,
            "password": body.password,
            "returnSecureToken": True,
        },
    )

    uid = auth["localId"]

    # Save the player profile in Firestore.
    try:
        db.collection("users").document(uid).set(
            {
                "uid": uid,
                "email": email,
                "display_name": display_name,
                "total_score": 0,
                "highest_level": 1,
                "created_at": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )
    except Exception as exc:
        print("Firestore profile creation failed:", repr(exc))
        raise HTTPException(
            status_code=503,
            detail=(
                "Firebase account was created, but its profile could "
                "not be saved. Try logging in to complete profile setup."
            ),
        ) from exc

    return {
        "success": True,
        "message": "Account created successfully.",
        "uid": uid,
        "email": email,
        "display_name": display_name,
        "id_token": auth["idToken"],
        "refresh_token": auth.get("refreshToken"),
    }


# --------------------------------------------------
# LOG IN
# --------------------------------------------------

@router.post("/login")
def login(body: LoginRequest):
    email = body.email.strip().lower()

    # Verify credentials through Firebase Authentication.
    auth = firebase_auth(
        "signInWithPassword",
        {
            "email": email,
            "password": body.password,
            "returnSecureToken": True,
        },
    )

    uid = auth["localId"]
    user_ref = db.collection("users").document(uid)

    # Get the existing profile or create a missing one.
    try:
        user_doc = user_ref.get()

        if user_doc.exists:
            profile = user_doc.to_dict()
            profile.update({
                "uid": uid,
                "email": email,
                "last_login": firestore.SERVER_TIMESTAMP,
            })
        else:
            profile = {
                "uid": uid,
                "email": email,
                "display_name": email.split("@")[0],
                "total_score": 0,
                "highest_level": 1,
                "created_at": firestore.SERVER_TIMESTAMP,
                "last_login": firestore.SERVER_TIMESTAMP,
            }

        user_ref.set(profile, merge=True)

    except Exception as exc:
        print("Firestore profile retrieval/update failed:", repr(exc))
        raise HTTPException(
            status_code=503,
            detail="Login succeeded, but the player profile could not be loaded.",
        ) from exc

    return {
        "success": True,
        "message": "Login successful.",
        "uid": uid,
        "email": email,
        "display_name": profile.get(
            "display_name",
            email.split("@")[0],
        ),
        "id_token": auth["idToken"],
        "refresh_token": auth.get("refreshToken"),
    }
