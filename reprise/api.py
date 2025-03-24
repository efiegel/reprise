from flask import Flask, jsonify, request
from flask_cors import CORS

from reprise.db import database_session
from reprise.repository import (
    CitationRepository,
    ClozeDeletionRepository,
    MotifRepository,
)
from reprise.service import Service

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


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
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "created_at": motif.created_at.isoformat(),
                    "citation": motif.citation.title if motif.citation else None,
                    "cloze_deletions": [
                        {"uuid": cd.uuid, "mask_tuples": cd.mask_tuples}
                        for cd in motif.cloze_deletions
                    ]
                    if motif.cloze_deletions
                    else None,
                }
                for motif in motifs
            ]
            return jsonify({"motifs": motifs_list, "total_count": total_count})

    if request.method == "POST":
        data = request.get_json()
        with database_session() as session:
            repository = MotifRepository(session)
            motif = repository.add_motif(data.get("content"))
            citation_title = data.get("citation")
            if citation_title:
                citation_repository = CitationRepository(session)
                citation = citation_repository.get_citation_by_title(citation_title)
                if not citation:
                    citation = citation_repository.add_citation(citation_title)
                motif = repository.add_citation(motif.uuid, citation)
            return jsonify(
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "citation": motif.citation.title if motif.citation else None,
                    "cloze_deletions": [
                        {"uuid": cd.uuid, "mask_tuples": cd.mask_tuples}
                        for cd in motif.cloze_deletions
                    ]
                    if motif.cloze_deletions
                    else None,
                    "created_at": motif.created_at.isoformat(),
                }
            )


@app.route("/motifs/<uuid>", methods=["PUT", "DELETE"])
def update_or_delete_motif(uuid):
    if request.method == "PUT":
        data = request.get_json()
        with database_session() as session:
            citation_title = data.get("citation")
            if citation_title:
                citation_repository = CitationRepository(session)
                citation = citation_repository.get_citation_by_title(citation_title)
                if not citation:
                    return jsonify(
                        {"error": f"Citation {citation_title} not found"}
                    ), 404

            repository = MotifRepository(session)
            motif = repository.update_motif_content(uuid, data["content"])

            if citation_title:
                motif = repository.add_citation(motif.uuid, citation)

            return jsonify(
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "citation": motif.citation.title if motif.citation else None,
                    "cloze_deletions": [
                        {"uuid": cd.uuid, "mask_tuples": cd.mask_tuples}
                        for cd in motif.cloze_deletions
                    ]
                    if motif.cloze_deletions
                    else None,
                    "created_at": motif.created_at.isoformat(),
                }
            )

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
                {
                    "uuid": citation.uuid,
                    "title": citation.title,
                    "created_at": citation.created_at.isoformat(),
                }
                for citation in citations
            ]
            return jsonify(citations_list)

    if request.method == "POST":
        data = request.get_json()
        with database_session() as session:
            repository = CitationRepository(session)
            citation = repository.add_citation(data.get("title"))
            return jsonify(
                {
                    "uuid": citation.uuid,
                    "title": citation.title,
                }
            )


@app.route("/reprise", methods=["POST"])
def reprise():
    with database_session() as session:
        service = Service(session)
        reprisals = service.reprise()
        reprisals_list = [
            {
                "uuid": reprisal.motif.uuid,  # motif uuid
                "content": reprisal.motif.content,
                "cloze_deletions": [
                    {
                        "uuid": reprisal.cloze_deletion.uuid,
                        "mask_tuples": reprisal.cloze_deletion.mask_tuples,
                    }
                    if reprisal.cloze_deletion
                    else None
                ]
                if reprisal.cloze_deletion
                else None,
                "created_at": reprisal.motif.created_at.isoformat(),
                "citation": reprisal.motif.citation.title
                if reprisal.motif.citation
                else None,
            }
            for reprisal in reprisals
        ]
        return jsonify(reprisals_list)


@app.route("/cloze_deletions", methods=["POST", "PUT"])
def cloze_deletions():
    data = request.get_json()
    with database_session() as session:
        repository = ClozeDeletionRepository(session)

        if request.method == "POST":
            motif_uuid = data.get("motif_uuid")
            mask_tuples = data.get("mask_tuples")
            cloze_deletion = repository.add_cloze_deletion(motif_uuid, mask_tuples)
            return jsonify(
                {
                    "uuid": cloze_deletion.uuid,
                    "mask_tuples": cloze_deletion.mask_tuples,
                }
            )

        if request.method == "PUT":
            cloze_deletion_uuid = data.get("uuid")
            mask_tuples = data.get("mask_tuples")
            cloze_deletion = repository.update_cloze_deletion(
                cloze_deletion_uuid, mask_tuples
            )
            return jsonify(
                {
                    "uuid": cloze_deletion.uuid,
                    "mask_tuples": cloze_deletion.mask_tuples,
                }
            )


@app.route("/cloze_deletions/<uuid>", methods=["DELETE"])
def delete_cloze_deletion(uuid):
    with database_session() as session:
        repository = ClozeDeletionRepository(session)
        repository.delete_cloze_deletion(uuid)
        return jsonify({"message": "Cloze deletion deleted"})
