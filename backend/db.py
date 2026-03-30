from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, Numeric, DateTime, func
from typing import AsyncGenerator
import json
from datetime import datetime
import uuid
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    database_url: str = "sqlite+aiosqlite:///./reports.db"

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    startup_name: Mapped[str] = mapped_column(Text, nullable=True)
    overall_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    investment_grade: Mapped[str] = mapped_column(Text, nullable=True)
    financial_risk: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    market_risk: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    founder_risk: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    extracted_claims: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    financial_metrics: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    red_flags: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    memo_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "startup_name": self.startup_name,
            "overall_risk_score": float(self.overall_risk_score or 0),
            "investment_grade": self.investment_grade,
            "financial_risk": float(self.financial_risk or 0),
            "market_risk": float(self.market_risk or 0),
            "founder_risk": float(self.founder_risk or 0),
            "extracted_claims": json.loads(self.extracted_claims or "{}"),
            "financial_metrics": json.loads(self.financial_metrics or "{}"),
            "red_flags": json.loads(self.red_flags or "[]"),
            "memo_text": self.memo_text,
            "created_at": self.created_at.isoformat(),
        }


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)