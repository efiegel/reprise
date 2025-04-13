from typing import Any, Dict, List

import logfire
from flask import Flask, jsonify
from flask_cors import CORS
from flask_pydantic import validate

from reprise import settings
from reprise.db import database_session
from reprise.repository import (
    CitationRepository,
    ClozeDeletionRepository,
    MotifRepository,
)
from reprise.schemas import (
    CitationCreate,
    CitationResponse,
    ClozeDeletionCreate,
    ClozeDeletionResponse,
    ClozeDeletionUpdate,
    DeleteResponse,
    ErrorResponse,
    MotifCreate,
    MotifListResponse,
    MotifResponse,
    MotifUpdate,
    PaginationParams,
)
from reprise.service import Service

app = Flask(__name__)


def configure_logfire():
    if settings.LOGFIRE_TOKEN:
        logfire.configure(token=settings.LOGFIRE_TOKEN)
        logfire.instrument_openai()


configure_logfire()
CORS(app)


@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"error": str(e)}), 400


@app.route("/motifs", methods=["GET"])
@validate(query=PaginationParams)
def get_motifs(query: PaginationParams) -> Dict[str, Any]:
    with database_session() as session:
        repository = MotifRepository(session)
        motifs = repository.get_motifs_paginated(query.page, query.page_size)
        total_count = repository.get_motifs_count()

        motifs_list = [
            MotifResponse(
                uuid=motif.uuid,
                content=motif.content,
                created_at=motif.created_at.isoformat(),
                citation=motif.citation.title if motif.citation else None,
                cloze_deletions=[
                    ClozeDeletionResponse(uuid=cd.uuid, mask_tuples=cd.mask_tuples)
                    for cd in motif.cloze_deletions
                ]
                if motif.cloze_deletions
                else None,
            ).model_dump()
            for motif in motifs
        ]
        return MotifListResponse(
            motifs=motifs_list, total_count=total_count
        ).model_dump()


@app.route("/motifs", methods=["POST"])
@validate(body=MotifCreate)
def create_motif(body: MotifCreate) -> Dict[str, Any]:
    with database_session() as session:
        repository = MotifRepository(session)
        motif = repository.add_motif(body.content)
        if body.citation:
            citation_repository = CitationRepository(session)
            citation = citation_repository.get_citation_by_title(body.citation)
            if not citation:
                citation = citation_repository.add_citation(body.citation)
            motif = repository.add_citation(motif.uuid, citation)

        # Generate cloze deletions for the motif
        if body.auto_generate_cloze_deletions:
            service = Service(session)
            try:
                service.cloze_delete_motif(motif.uuid, n_max=2)
            except Exception as e:
                app.logger.error(f"Error generating cloze deletions: {e}")
                return jsonify({"error": str(e)}), 500

            # Refresh motif to incorporate cloze deletions
            session.refresh(motif)

        response = MotifResponse(
            uuid=motif.uuid,
            content=motif.content,
            citation=motif.citation.title if motif.citation else None,
            cloze_deletions=[
                ClozeDeletionResponse(uuid=cd.uuid, mask_tuples=cd.mask_tuples)
                for cd in motif.cloze_deletions
            ]
            if motif.cloze_deletions
            else None,
            created_at=motif.created_at.isoformat(),
        )
        return response.model_dump()


@app.route("/motifs/<uuid>", methods=["PUT"])
@validate(body=MotifUpdate)
def update_motif(uuid: str, body: MotifUpdate) -> Dict[str, Any]:
    with database_session() as session:
        if body.citation:
            citation_repository = CitationRepository(session)
            citation = citation_repository.get_citation_by_title(body.citation)
            if not citation:
                return ErrorResponse(
                    error=f"Citation {body.citation} not found"
                ).model_dump(), 404

        repository = MotifRepository(session)
        motif = repository.update_motif_content(uuid, body.content)

        if body.citation:
            motif = repository.add_citation(motif.uuid, citation)

        response = MotifResponse(
            uuid=motif.uuid,
            content=motif.content,
            citation=motif.citation.title if motif.citation else None,
            cloze_deletions=[
                ClozeDeletionResponse(uuid=cd.uuid, mask_tuples=cd.mask_tuples)
                for cd in motif.cloze_deletions
            ]
            if motif.cloze_deletions
            else None,
            created_at=motif.created_at.isoformat(),
        )
        return response.model_dump()


@app.route("/motifs/<uuid>", methods=["DELETE"])
def delete_motif(uuid: str) -> Dict[str, str]:
    with database_session() as session:
        repository = MotifRepository(session)
        repository.delete_motif(uuid)
    return DeleteResponse(message="Motif deleted").model_dump()


@app.route("/citations", methods=["GET"])
def get_citations() -> List[Dict[str, Any]]:
    with database_session() as session:
        repository = CitationRepository(session)
        citations = repository.get_citations()
        citations_list = [
            CitationResponse(
                uuid=citation.uuid,
                title=citation.title,
                created_at=citation.created_at.isoformat(),
            ).model_dump()
            for citation in citations
        ]
        return citations_list


@app.route("/citations", methods=["POST"])
@validate(body=CitationCreate)
def create_citation(body: CitationCreate) -> Dict[str, Any]:
    with database_session() as session:
        repository = CitationRepository(session)
        citation = repository.add_citation(body.title)
        response = CitationResponse(
            uuid=citation.uuid,
            title=citation.title,
        )
        return response.model_dump()


@app.route("/reprise", methods=["POST"])
def reprise() -> List[Dict[str, Any]]:
    with database_session() as session:
        service = Service(session)
        reprisals = service.reprise()
        reprisals_list = [
            MotifResponse(
                uuid=reprisal.motif.uuid,
                content=reprisal.motif.content,
                cloze_deletions=[
                    ClozeDeletionResponse(
                        uuid=reprisal.cloze_deletion.uuid,
                        mask_tuples=reprisal.cloze_deletion.mask_tuples,
                    )
                ]
                if reprisal.cloze_deletion
                else None,
                created_at=reprisal.motif.created_at.isoformat(),
                citation=reprisal.motif.citation.title
                if reprisal.motif.citation
                else None,
            ).model_dump()
            for reprisal in reprisals
        ]
        return reprisals_list


@app.route("/cloze_deletions", methods=["POST"])
@validate(body=ClozeDeletionCreate)
def create_cloze_deletion(body: ClozeDeletionCreate) -> Dict[str, Any]:
    with database_session() as session:
        repository = ClozeDeletionRepository(session)
        cloze_deletion = repository.add_cloze_deletion(
            body.motif_uuid, body.mask_tuples
        )
        response = ClozeDeletionResponse(
            uuid=cloze_deletion.uuid,
            mask_tuples=cloze_deletion.mask_tuples,
        )
        return response.model_dump()


@app.route("/cloze_deletions", methods=["PUT"])
@validate(body=ClozeDeletionUpdate)
def update_cloze_deletion(body: ClozeDeletionUpdate) -> Dict[str, Any]:
    with database_session() as session:
        repository = ClozeDeletionRepository(session)
        cloze_deletion = repository.update_cloze_deletion(body.uuid, body.mask_tuples)
        response = ClozeDeletionResponse(
            uuid=cloze_deletion.uuid,
            mask_tuples=cloze_deletion.mask_tuples,
        )
        return response.model_dump()


@app.route("/cloze_deletions/<uuid>", methods=["DELETE"])
def delete_cloze_deletion(uuid: str) -> Dict[str, str]:
    with database_session() as session:
        repository = ClozeDeletionRepository(session)
        repository.delete_cloze_deletion(uuid)
        return DeleteResponse(message="Cloze deletion deleted").model_dump()
