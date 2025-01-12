from flask import Flask, jsonify

from .db import Motif, database_context

app = Flask(__name__)


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
