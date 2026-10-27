from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import database
from .ai_service import run_analysis
from .config import BASE_DIR
from .schemas import AnalyzeRequest

STATIC_DIR = Path(BASE_DIR) / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="TalentVerse — Skills & Career Intelligence", version="1.0.0", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError):
    messages = []
    for err in exc.errors():
        msg = str(err.get("msg", "Invalid input")).replace("Value error, ", "")
        messages.append(msg)
    return JSONResponse(status_code=422, content={"detail": " ".join(messages) or "Invalid input."})


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TalentVerse"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    try:
        result, processing_mode, warning = run_analysis(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")
    try:
        saved = database.insert_record(request.mode, result.get("target_role", ""), request.input_text,
                                       request.profile_text, result, processing_mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not save to database: {exc}")
    return {"saved": True, "id": saved["id"], "created_at": saved["created_at"], "mode": request.mode,
            "processing_mode": processing_mode, "warning": warning, "result": result}


@app.get("/api/profiles")
def list_profiles():
    return {"items": database.list_records()}


@app.get("/api/profiles/{record_id}")
def get_profile(record_id: int):
    record = database.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    return record


@app.delete("/api/profiles/{record_id}")
def delete_profile(record_id: int):
    if not database.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Record not found.")
    return {"deleted": True, "id": record_id}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
