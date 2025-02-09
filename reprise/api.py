from flask import Flask, jsonify, request
from flask_cors import CORS

from .db import Motif, database_session

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/motifs", methods=["GET", "POST"])
def motifs():
    if request.method == "GET":
        with database_session() as session:
            motifs = session.query(Motif).all()
            motifs_list = [
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "created_at": motif.created_at.isoformat(),
                    "citation": motif.citation,
                }
                for motif in motifs
            ]
            return jsonify(motifs_list)

    if request.method == "POST":
        data = request.get_json()
        with database_session() as session:
            motif = Motif(content=data["content"])
            session.add(motif)
            session.commit()
            return jsonify(
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "created_at": motif.created_at.isoformat(),
                    "citation": motif.citation,
                }
            )


@app.route("/motifs/<uuid>", methods=["PUT", "DELETE"])
def update_or_delete_motif(uuid):
    if request.method == "PUT":
        data = request.get_json()
        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=uuid).one_or_none()
            motif.content = data["content"]
            session.commit()
            return jsonify(
                {
                    "uuid": motif.uuid,
                    "content": motif.content,
                    "created_at": motif.created_at.isoformat(),
                    "citation": motif.citation,
                }
            )

    if request.method == "DELETE":
        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=uuid).one_or_none()
            session.delete(motif)
            session.commit()
        return jsonify({"message": "Motif deleted"})


if __name__ == "__main__":
    app.run(debug=True)
