from typing import Any, Dict, List, Optional, Tuple, Type, Union

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, ValidationError

from reprise.db import database_session
from reprise.repository import (
    CitationRepository,
    ClozeDeletionRepository,
    MotifRepository,
)
from reprise.service import Service


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


# Helper function for handling validation errors
def validate_request_data(
    model_class: Type[BaseModel], data: Dict[str, Any]
) -> Union[BaseModel, tuple]:
    try:
        return model_class(**data)
    except ValidationError as e:
        return {"errors": e.errors()}, 400


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Add error handler for malformed JSON
@app.errorhandler(400)
def handle_bad_request(e):
    if "Failed to decode JSON object" in str(e):
        return jsonify({"error": "Malformed JSON in request"}), 400
    return jsonify({"error": str(e)}), 400


@app.route("/motifs", methods=["GET", "POST"])
def motifs():
    if request.method == "GET":
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        with database_session() as session:
            repository = MotifRepository(session)
            motifs = repository.get_motifs_paginated(page, page_size)
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
            return jsonify({"motifs": motifs_list, "total_count": total_count})

    if request.method == "POST":
        validated_data = validate_request_data(MotifCreate, request.get_json())
        if isinstance(validated_data, tuple):  # Error response
            return jsonify(validated_data[0]), validated_data[1]

        data = validated_data
        with database_session() as session:
            repository = MotifRepository(session)
            motif = repository.add_motif(data.content)
            if data.citation:
                citation_repository = CitationRepository(session)
                citation = citation_repository.get_citation_by_title(data.citation)
                if not citation:
                    citation = citation_repository.add_citation(data.citation)
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
            return jsonify(response.model_dump())


@app.route("/motifs/<uuid>", methods=["PUT", "DELETE"])
def update_or_delete_motif(uuid):
    if request.method == "PUT":
        validated_data = validate_request_data(MotifUpdate, request.get_json())
        if isinstance(validated_data, tuple):  # Error response
            return jsonify(validated_data[0]), validated_data[1]

        data = validated_data
        with database_session() as session:
            if data.citation:
                citation_repository = CitationRepository(session)
                citation = citation_repository.get_citation_by_title(data.citation)
                if not citation:
                    return jsonify(
                        {"error": f"Citation {data.citation} not found"}
                    ), 404

            repository = MotifRepository(session)
            motif = repository.update_motif_content(uuid, data.content)

            if data.citation:
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
            return jsonify(response.model_dump())

    if request.method == "DELETE":
        with database_session() as session:
            repository = MotifRepository(session)
            repository.delete_motif(uuid)
        return jsonify({"message": "Motif deleted"})


@app.route("/citations", methods=["GET", "POST"])
def create_citation():
    if request.method == "GET":
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
            return jsonify(citations_list)

    if request.method == "POST":
        validated_data = validate_request_data(CitationCreate, request.get_json())
        if isinstance(validated_data, tuple):  # Error response
            return jsonify(validated_data[0]), validated_data[1]

        data = validated_data
        with database_session() as session:
            repository = CitationRepository(session)
            citation = repository.add_citation(data.title)
            response = CitationResponse(
                uuid=citation.uuid,
                title=citation.title,
            )
            return jsonify(response.model_dump())


@app.route("/reprise", methods=["POST"])
def reprise():
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
        return jsonify(reprisals_list)


@app.route("/cloze_deletions", methods=["POST", "PUT"])
def cloze_deletions():
    if request.method == "POST":
        validated_data = validate_request_data(ClozeDeletionCreate, request.get_json())
        if isinstance(validated_data, tuple):  # Error response
            return jsonify(validated_data[0]), validated_data[1]

        data = validated_data
        with database_session() as session:
            repository = ClozeDeletionRepository(session)
            cloze_deletion = repository.add_cloze_deletion(
                data.motif_uuid, data.mask_tuples
            )
            response = ClozeDeletionResponse(
                uuid=cloze_deletion.uuid,
                mask_tuples=cloze_deletion.mask_tuples,
            )
            return jsonify(response.model_dump())

    if request.method == "PUT":
        validated_data = validate_request_data(ClozeDeletionUpdate, request.get_json())
        if isinstance(validated_data, tuple):  # Error response
            return jsonify(validated_data[0]), validated_data[1]

        data = validated_data
        with database_session() as session:
            repository = ClozeDeletionRepository(session)
            cloze_deletion = repository.update_cloze_deletion(
                data.uuid, data.mask_tuples
            )
            response = ClozeDeletionResponse(
                uuid=cloze_deletion.uuid,
                mask_tuples=cloze_deletion.mask_tuples,
            )
            return jsonify(response.model_dump())


@app.route("/cloze_deletions/<uuid>", methods=["DELETE"])
def delete_cloze_deletion(uuid):
    with database_session() as session:
        repository = ClozeDeletionRepository(session)
        repository.delete_cloze_deletion(uuid)
        return jsonify({"message": "Cloze deletion deleted"})
