import os
from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

database = os.getenv("DATABASE_URL", "sqlite:///reprise.db")
engine = create_engine(database, echo=False)

Base = declarative_base()
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def database_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.commit()
        session.close()


class Motif(Base):
    __tablename__ = "motif"

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    content = Column(Text, nullable=False)
    citation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
