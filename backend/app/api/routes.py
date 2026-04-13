from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.database import get_database
from app.core.security import get_current_user
from app.models.schemas import DashboardStats, NLPQueryRequest, NLPQueryResponse, PredictionResponse, SensorPayload, SensorRecord
from app.services.analytics import clamp_fill_percentage, day_bounds
from app.services.classifier import classifier
from app.services.cloud_storage import upload_image_to_gridfs
from app.services.nlp import nlp_service

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "EcoVision AI",
        "cloud_provider": settings.cloud_provider,
        "storage_backend": settings.storage_backend,
    }


@router.post("/sensor", response_model=SensorRecord)
async def ingest_sensor(payload: SensorPayload, db=Depends(get_database)):
    fill_percentage = clamp_fill_percentage(payload.distance_cm, payload.max_depth_cm)
    doc = {
        "bin_id": payload.bin_id,
        "distance_cm": payload.distance_cm,
        "fill_percentage": fill_percentage,
        "location": payload.location,
        "created_at": datetime.now(timezone.utc),
    }
    await db.sensor_readings.insert_one(doc)
    return SensorRecord(**doc)


@router.post("/predict", response_model=PredictionResponse)
async def predict_waste(
    file: UploadFile = File(...),
    location: str = Form(default="Campus Block A"),
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    extension = Path(file.filename).suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(status_code=400, detail="Only JPG/PNG files are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    save_path = UPLOAD_DIR / f"{datetime.now(timezone.utc).timestamp()}_{file.filename}"
    with save_path.open("wb") as buffer:
        buffer.write(file_bytes)

    waste_type, confidence = classifier.predict_image(str(save_path))

    cloud_file_id = None
    cloud_url = None
    if settings.storage_backend == "gridfs":
        file_id = await upload_image_to_gridfs(
            db,
            save_path.name,
            file.content_type or "image/jpeg",
            file_bytes,
        )
        cloud_file_id = str(file_id)
        cloud_url = f"gridfs://waste_images/{cloud_file_id}"

    record = {
        "filename": save_path.name,
        "waste_type": waste_type,
        "confidence": confidence,
        "location": location,
        "storage_backend": settings.storage_backend,
        "cloud_file_id": cloud_file_id,
        "cloud_url": cloud_url,
        "file_size_bytes": len(file_bytes),
        "uploaded_by": current_user["_id"],
        "created_at": datetime.now(timezone.utc),
    }
    await db.waste_predictions.insert_one(record)

    if settings.storage_backend == "gridfs" and save_path.exists():
        save_path.unlink()

    return PredictionResponse(
        waste_type=waste_type,
        confidence=confidence,
        location=location,
        filename=save_path.name,
        storage_backend=settings.storage_backend,
        cloud_file_id=cloud_file_id,
        cloud_url=cloud_url,
    )


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(current_user=Depends(get_current_user), db=Depends(get_database)):
    total_waste_items = await db.waste_predictions.count_documents({})

    distribution_cursor = db.waste_predictions.find({}, {"waste_type": 1, "_id": 0})
    distribution_items = [item async for item in distribution_cursor]
    counter = Counter(item["waste_type"] for item in distribution_items)
    distribution = {
        "plastic": counter.get("plastic", 0),
        "metal": counter.get("metal", 0),
        "organic": counter.get("organic", 0),
    }

    latest_sensor = await db.sensor_readings.find_one(sort=[("created_at", -1)])
    latest_fill = float(latest_sensor["fill_percentage"]) if latest_sensor else 0.0
    latest_location = latest_sensor["location"] if latest_sensor else "Unknown"

    start, end = day_bounds(datetime.now(timezone.utc))
    trend_pipeline = [
        {"$match": {"created_at": {"$gte": start, "$lt": end}}},
        {
            "$group": {
                "_id": {"$hour": "$created_at"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    trend = [doc async for doc in db.waste_predictions.aggregate(trend_pipeline)]
    daily_trend = [{"hour": f"{d['_id']:02d}:00", "count": d["count"]} for d in trend]

    cloud_images_count = await db.waste_predictions.count_documents({
        "storage_backend": "gridfs",
        "cloud_file_id": {"$ne": None},
    })
    total_bytes = 0
    if settings.storage_backend == "gridfs":
        size_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$length"}}}]
        size_docs = [doc async for doc in db["waste_images.files"].aggregate(size_pipeline)]
        if size_docs:
            total_bytes = int(size_docs[0].get("total", 0))

    return DashboardStats(
        total_waste_items=total_waste_items,
        distribution=distribution,
        latest_fill_percentage=latest_fill,
        is_bin_full=latest_fill > 90,
        daily_trend=daily_trend,
        latest_location=latest_location,
        cloud_provider=settings.cloud_provider,
        storage_backend=settings.storage_backend,
        cloud_images_count=cloud_images_count,
        cloud_storage_mb=round(total_bytes / (1024 * 1024), 3),
    )


@router.post("/query", response_model=NLPQueryResponse)
async def query_nlp(payload: NLPQueryRequest, current_user=Depends(get_current_user), db=Depends(get_database)):
    answer, intent = await nlp_service.answer(db, payload.query)
    return NLPQueryResponse(answer=answer, intent=intent)
