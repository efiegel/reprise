from flask import Flask, jsonify, request
from flask_cors import CORS

from .db import Motif, database_context

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/motifs", methods=["GET", "POST"])
def motifs():
    if request.method == "GET":
        with database_context():
            motifs = Motif.select()
            motifs_list = [
                {"uuid": motif.uuid, "content": motif.content} for motif in motifs
            ]
        return jsonify(motifs_list)

    if request.method == "POST":
        data = request.get_json()
        with database_context():
            motif = Motif.create(content=data["content"])
        return jsonify({"uuid": motif.uuid, "content": motif.content})


@app.route("/motifs/<uuid>", methods=["PUT", "DELETE"])
def update_or_delete_motif(uuid):
    if request.method == "PUT":
        data = request.get_json()
        with database_context():
            motif = Motif.get(Motif.uuid == uuid)
            motif.content = data["content"]
            motif.save()
        return jsonify({"uuid": motif.uuid, "content": motif.content})

    if request.method == "DELETE":
        with database_context():
            motif = Motif.get(Motif.uuid == uuid)
            motif.delete_instance()
        return jsonify({"message": "Motif deleted"})


if __name__ == "__main__":
    app.run(debug=True)
