"""
Configuração de Conexão com Banco de Dados Relacional (SQLAlchemy 2.0).
Suporta SQLite por padrão (zero-config para avaliação) ou PostgreSQL via variável DATABASE_URL.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./deslocai.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency Injection generator para sessões de banco de dados no FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
