from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def database_context():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class Motif(Base):
    __tablename__ = "motif"

    uuid = Column(String(36), primary_key=True, default=str(uuid4()))
    content = Column(Text, nullable=False)
    citation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
