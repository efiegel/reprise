from flask import Flask, jsonify, request
from flask_cors import CORS

from reprise.db import database_session
from reprise.repository import CitationRepository, MotifRepository
from reprise.service import Service

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/motifs", methods=["GET", "POST"])
def motifs():
    if request.method == "GET":
        with database_session() as session:
            repository = MotifRepository(session)
            motifs = repository.get_motifs()
            motifs_list = [
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "created_at": motif.created_at.isoformat(),
                    "citation": motif.citation.title if motif.citation else None,
                }
                for motif in motifs
            ]
            return jsonify(motifs_list)

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
        reprised_motifs = service.reprise_motifs()
        motifs_list = [
            {
                "uuid": motif.uuid,
                "content": motif.content,
                "created_at": motif.created_at.isoformat(),
                "citation": motif.citation.title if motif.citation else None,
            }
            for motif in reprised_motifs
        ]
        return jsonify(motifs_list)
