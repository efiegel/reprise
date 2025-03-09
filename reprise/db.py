import os
from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.schema import ForeignKey

database = os.getenv("DATABASE_URL", "sqlite:///reprise.db")
engine = create_engine(database, echo=False)

Base = declarative_base()

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
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    citation_uuid = Column(String(36), ForeignKey("citation.uuid"), nullable=True)

    citation = relationship("Citation", backref="motifs")


class Citation(Base):
    __tablename__ = "citation"

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)


class Reprisal(Base):
    __tablename__ = "reprisal"

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    motif_uuid = Column(String(36), ForeignKey("motif.uuid"), nullable=False)
    set_uuid = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    motif = relationship("Motif", backref="reprisals")
