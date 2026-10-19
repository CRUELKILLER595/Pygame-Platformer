import json
from pathlib import Path
import re
from firebase_admin import firestore
from firebase_client import db

BASE_DIR = Path(__file__).resolve().parent
LEVELS_DIR = BASE_DIR.parent / "levels"
def main():
    if not LEVELS_DIR.is_dir():
        raise FileNotFoundError(
            f"Levels directory not found: {LEVELS_DIR}"
        )

    json_files = sorted(LEVELS_DIR.glob("*.json"))

    print(f"Levels directory: {LEVELS_DIR}")
    print(f"Found {len(json_files)} JSON files:")

    uploaded = 0

    for file_path in json_files:
        content = file_path.read_text(encoding="utf-8")
        level_data = None
        parse_error = None

        if not content.strip():
            parse_status = "empty"
        else:
            try:
                level_data = json.loads(content)
                parse_status = "valid"
            except json.JSONDecodeError as exc:
                parse_status = "invalid"
                parse_error = (
                    f"Line {exc.lineno}, column {exc.colno}: {exc.msg}"
                )

        doc_id = re.sub(
            r"[^a-z0-9_-]",
            "_",
            file_path.stem.lower()
        )

        record = {
            "title": file_path.stem.replace("_", " ").title(),
            "source_filename": file_path.name,
            "level_data": level_data,
            "source_text": content,
            "parse_status": parse_status,
            "is_playable": parse_status == "valid",
            "visible_in_level_select": True,
            "status": (
                "published" if parse_status == "valid"
                else "needs_repair"
            ),
        }

        if parse_error:
            record["parse_error"] = parse_error

        db.collection("levels").document(doc_id).set(record)

        uploaded += 1
        print(
            f"UPLOADED: {file_path.name} "
            f"| status={parse_status} "
            f"| playable={record['is_playable']}"
        )

        if parse_error:
            print(f"  Problem: {parse_error}")

    print(f"\nUpload complete: {uploaded}/{len(json_files)} files.")

if __name__ == "__main__":
    main()