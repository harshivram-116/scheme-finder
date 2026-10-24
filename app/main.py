from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.eligibility import Profile, check_eligibility

app = FastAPI(title="Scheme Finder API")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class ProfileIn(BaseModel):
    age: int = Field(ge=0, le=120)
    gender: str
    annual_income: int = Field(ge=0)
    is_bpl: bool = False
    owns_agri_land: bool = False
    is_student: bool = False
    district: Optional[str] = None


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/eligibility")
def eligibility(p: ProfileIn):
    return check_eligibility(Profile(**p.model_dump()))
