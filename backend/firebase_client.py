
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Locate the backend folder and load its .env file.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Read the Firebase service-account path.
key_path = os.getenv("FIREBASE_CREDENTIALS")

if not key_path:
    raise RuntimeError(
        "FIREBASE_CREDENTIALS is missing from the .env file."
    )

key_file = Path(key_path)

# Allow relative paths as well as absolute paths.
if not key_file.is_absolute():
    key_file = BASE_DIR / key_file

if not key_file.is_file():
    raise FileNotFoundError(
        f"Firebase service-account file not found: {key_file}"
    )

# Initialize Firebase only if it has not already been initialized.
try:
    app = firebase_admin.get_app()
except ValueError:
    certificate = credentials.Certificate(str(key_file))
    app = firebase_admin.initialize_app(certificate)

# Firestore database connection.
db = firestore.client(app=app)
