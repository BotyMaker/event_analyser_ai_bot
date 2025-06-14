from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import BigInteger, DateTime, String, Text, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

from .config import config


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    language: Mapped[str] = mapped_column(String(5), default="en")
    custom_instruction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class News(Base):
    __tablename__ = "news"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(1024))
    content: Mapped[str] = mapped_column(Text)
    published_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    claims_extracted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    claims: Mapped[list["Claim"]] = relationship("Claim", back_populates="news", cascade="all, delete-orphan")


class Claim(Base):
    __tablename__ = "claims"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    news: Mapped["News"] = relationship("News", back_populates="claims")


class UserCreate(BaseModel):
    telegram_id: int
    language: str = "en"
    custom_instruction: Optional[str] = None


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    telegram_id: int
    language: str
    custom_instruction: Optional[str]
    created_at: datetime
    updated_at: datetime


class NewsCreate(BaseModel):
    url: str
    title: str
    content: str
    published_date: Optional[str] = None


class NewsResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    url: str
    title: str
    content: str
    published_date: Optional[str]
    claims_extracted: bool
    created_at: datetime


class ClaimCreate(BaseModel):
    text: str


class ClaimResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    text: str
    created_at: datetime


# Force sync SQLite with explicit driver
db_url = config.database_url
if db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+pysqlite:///")
elif db_url.startswith("sqlite://"):
    db_url = db_url.replace("sqlite://", "sqlite+pysqlite:///")

engine = create_engine(db_url, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine) 