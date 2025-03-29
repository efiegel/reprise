from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel


# Pydantic schemas for request validation
class CitationCreate(BaseModel):
    title: str


class CitationResponse(BaseModel):
    uuid: str
    title: str
    created_at: Optional[str] = None


class ClozeDeletionCreate(BaseModel):
    motif_uuid: str
    mask_tuples: List[Tuple[int, int]]


class ClozeDeletionUpdate(BaseModel):
    uuid: str
    mask_tuples: List[Tuple[int, int]]


class ClozeDeletionResponse(BaseModel):
    uuid: str
    mask_tuples: List[Tuple[int, int]]


class MotifCreate(BaseModel):
    content: str
    citation: Optional[str] = None


class MotifUpdate(BaseModel):
    content: str
    citation: Optional[str] = None


class MotifResponse(BaseModel):
    uuid: str
    content: str
    created_at: str
    citation: Optional[str] = None
    cloze_deletions: Optional[List[ClozeDeletionResponse]] = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10


class MotifListResponse(BaseModel):
    motifs: List[Dict[str, Any]]
    total_count: int


class CitationListResponse(BaseModel):
    citations: List[CitationResponse]


class DeleteResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
