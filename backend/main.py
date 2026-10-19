from fastapi import FastAPI, HTTPException
from firebase_client import db
from auth_routes import router as auth_router
app = FastAPI(title="PixelBound API")
app.include_router(auth_router)

@app.get("/status")
def health_check():
    try:
        db.collection("levels").limit(1).get()
        return {
            "api": "running",
            "firestore": "connected"
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Firestore connection failed"
        ) from exc
@app.get("/levels/published")
def get_published_levels():
    try:
        documents = (
            db.collection("levels")
            .where("status", "==", "published")
            .limit(20)
            .stream()
        )

        levels = []

        for document in documents:
            level_data = document.to_dict()
            level_data["id"] = document.id
            levels.append(level_data)

        return {"levels": levels}

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve published levels"
        ) from exc
@app.get("/levels/catalog")
def get_level_catalog():
    try:
        documents = (
            db.collection("levels")
            .where("visible_in_level_select", "==", True)
            .stream()
        )

        levels = []

        for document in documents:
            data = document.to_dict()

            levels.append({
                "id": document.id,
                "title": data.get("title", document.id),
                "playable": data.get("is_playable", False),
                "parse_status": data.get("parse_status", "unknown"),
                "status": data.get("status", "unknown"),
            })

        levels.sort(key=lambda level: level["id"])

        return {"levels": levels}

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve level catalogue",
        ) from exc
@app.get("/levels/{level_id}/data")
def get_level_data(level_id: str):
    try:
        document = (
            db.collection("levels")
            .document(level_id)
            .get()
        )

        if not document.exists:
            raise HTTPException(
                status_code=404,
                detail="Level not found",
            )

        data = document.to_dict()

        if not data.get("visible_in_level_select", False):
            raise HTTPException(
                status_code=404,
                detail="Level not available",
            )

        if not data.get("is_playable", False):
            raise HTTPException(
                status_code=409,
                detail="This level needs repair before playing",
            )

        return {
            "id": document.id,
            "title": data.get("title", document.id),
            "level_data": data["level_data"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load level",
        ) from exc