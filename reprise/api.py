from flask import Flask, jsonify, request
from flask_cors import CORS

from reprise.repository import add_motif
from settings import VAULT_DIRECTORY

from .db import Motif, database_context
from .llm import Agent
from .vault import Vault

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

vault = Vault(VAULT_DIRECTORY)
agent = Agent(model_name="gpt-4o-mini")
diff_iterator = vault.diff_iterator()
current_diff = None


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/motifs", methods=["GET", "POST"])
def motifs():
    if request.method == "GET":
        with database_context():
            motifs = Motif.select()
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
        with database_context():
            motif = Motif.create(content=data["content"])
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
        with database_context():
            motif = Motif.get(Motif.uuid == uuid)
            motif.content = data["content"]
            motif.save()
        return jsonify(
            {
                "uuid": motif.uuid,
                "content": motif.content,
                "created_at": motif.created_at.isoformat(),
                "citation": motif.citation,
            }
        )

    if request.method == "DELETE":
        with database_context():
            motif = Motif.get(Motif.uuid == uuid)
            motif.delete_instance()
        return jsonify({"message": "Motif deleted"})


@app.route("/diff-snippets", methods=["GET"])
def get_diff_snippets():
    global current_diff
    try:
        current_diff = next(diff_iterator)
        snippets = agent.extract_information(current_diff)
        return jsonify(snippets)
    except StopIteration:
        return jsonify({"message": "No more diffs"}), 404


@app.route("/validate-snippets", methods=["POST"])
def validate_snippets():
    data = request.get_json()
    validated_snippets = data.get("snippets", [])
    with database_context():
        for snippet in validated_snippets:
            add_motif(snippet, None)
    return jsonify({"message": "Snippets validated and saved"})


if __name__ == "__main__":
    app.run(debug=True)
