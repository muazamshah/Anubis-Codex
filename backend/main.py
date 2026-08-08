from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.repository import router as repository_router
from api.routes.phase2 import router as phase2_router
from api.routes.phase3 import router as phase3_router

app = FastAPI(title="ANUBIS CODEX", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repository_router)
app.include_router(phase2_router)
app.include_router(phase3_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "anubis-codex", "phase": "Phase 1 + Phase 2 + Phase 3"}
