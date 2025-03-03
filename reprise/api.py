from flask import Flask, jsonify, request
from flask_cors import CORS

from reprise.db import database_session
from reprise.repository import MotifRepository

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
            return jsonify(
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "created_at": motif.created_at.isoformat(),
                }
            )


@app.route("/motifs/<uuid>", methods=["PUT", "DELETE"])
def update_or_delete_motif(uuid):
    if request.method == "PUT":
        data = request.get_json()
        with database_session() as session:
            repository = MotifRepository(session)
            motif = repository.update_motif_content(uuid, data["content"])
            return jsonify(
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "created_at": motif.created_at.isoformat(),
                }
            )

    if request.method == "DELETE":
        with database_session() as session:
            repository = MotifRepository(session)
            repository.delete_motif(uuid)
        return jsonify({"message": "Motif deleted"})
