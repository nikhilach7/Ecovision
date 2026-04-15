from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

WasteType = Literal["plastic", "metal", "organic"]
TrashNetLabel = Literal["glass", "paper", "cardboard", "plastic", "metal", "trash"]


class SensorPayload(BaseModel):
    bin_id: str = Field(default="BIN-01")
    distance_cm: float = Field(ge=0)
    max_depth_cm: float = Field(default=40.0, gt=0)
    location: str = Field(default="Campus Block A")


class SensorRecord(BaseModel):
    bin_id: str
    distance_cm: float
    fill_percentage: float
    location: str
    created_at: datetime


class PredictionResponse(BaseModel):
    waste_type: WasteType
    predicted_label: TrashNetLabel | WasteType | Literal["unknown"]
    confidence: float
    location: str
    filename: str
    storage_backend: str
    cloud_file_id: str | None = None
    cloud_url: str | None = None


class NLPQueryRequest(BaseModel):
    query: str


class NLPQueryResponse(BaseModel):
    answer: str
    intent: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class DashboardStats(BaseModel):
    total_waste_items: int
    distribution: dict[str, int]
    latest_fill_percentage: float
    is_bin_full: bool
    daily_trend: list[dict]
    latest_location: str
    cloud_provider: str
    storage_backend: str
    cloud_images_count: int
    cloud_storage_mb: float


class RegisterRequest(BaseModel):
    email: str
    full_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
