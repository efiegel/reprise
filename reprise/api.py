from flask import Flask, jsonify, request
from flask_cors import CORS

from .db import Motif, database_context

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/motifs", methods=["GET"])
def get_motifs():
    with database_context():
        motifs = Motif.select()
        motifs_list = [
            {"uuid": motif.uuid, "content": motif.content} for motif in motifs
        ]
    return jsonify(motifs_list)


@app.route("/motifs/<uuid>", methods=["PUT"])
def update_motif(uuid):
    data = request.get_json()
    with database_context():
        motif = Motif.get(Motif.uuid == uuid)
        motif.content = data["content"]
        motif.save()
    return jsonify({"uuid": motif.uuid, "content": motif.content})
