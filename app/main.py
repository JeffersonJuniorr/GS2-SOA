"""
Entrypoint da Aplicação Backend SOA & Web Services — CitizenTech Deslocai.
Executa migrações automáticas e seed de dados reais na inicialização.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database import SessionLocal
from app.infrastructure.migrations import run_migrations
from app.infrastructure.seed import seed_initial_data
from app.presentation.routes import router as api_router
from app.presentation.dashboard import dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        run_migrations(db)
        seed_initial_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Deslocai CitizenTech — SOA & Web Services API",
    description=(
        "Camada de Backend Orientada a Serviços (SOA) da CitizenTech **Deslocai** (3ES - FIAP 2026).\n\n"
        "- **Problema resolvido:** Superlotação imprevisível, calor extremo nos vagões/pontos e falta de "
        "avisos em tempo real sobre equipamentos de acessibilidade quebrados (elevadores e escadas rolantes).\n"
        "- **Integrações nativas:** Recebe telemetria IoT do **ESP32 (Wokwi)** e consome o modelo preditivo "
        "**Random Forest** treinado com dados públicos reais (**Portal SP156 + INMET 2024**).\n"
        "- **ODS Conectados:** ODS 9, ODS 10 e ODS 11."
    ),
    version="1.0.0",
    contact={
        "name": "Equipe Deslocai - Engenharia de Software (3ES FIAP)",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(api_router)
