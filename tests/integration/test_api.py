from datetime import datetime
from uuid import uuid4

from flask import json

from reprise.db import Motif, database_context


class TestAPI:
    def test_get_motifs(self, session, client):
        motif = Motif(content="Test content", citation="Test citation")
        session.add(motif)
        session.commit()

        response = client.get("/motifs")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["content"] == "Test content"
        assert data[0]["citation"] == "Test citation"

    def test_add_motif(self, session, client):
        response = client.post(
            "/motifs",
            data=json.dumps({"content": "New motif content"}),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["content"] == "New motif content"

        motif = session.query(Motif).filter_by(uuid=data["uuid"]).one_or_none()
        assert motif.content == "New motif content"

    def test_update_motif(self, session, client):
        motif = Motif(
            uuid=str(uuid4()),
            content="Old content",
            citation="Old citation",
            created_at=datetime.now(),
        )
        session.add(motif)
        session.commit()

        response = client.put(
            f"/motifs/{motif.uuid}",
            data=json.dumps({"content": "Updated content"}),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["content"] == "Updated content"

        with database_context() as new_session:
            motif = new_session.query(Motif).filter_by(uuid=motif.uuid).one_or_none()
            assert motif.content == "Updated content"

    def test_delete_motif(self, session, client):
        motif = Motif(
            uuid=str(uuid4()),
            content="Content to delete",
            citation="Citation to delete",
            created_at=datetime.now(),
        )
        session.add(motif)
        session.commit()

        response = client.delete(f"/motifs/{motif.uuid}")

        assert response.status_code == 200
        assert json.loads(response.data)["message"] == "Motif deleted"

        with database_context() as new_session:
            assert len(new_session.query(Motif).filter_by(uuid=motif.uuid).all()) == 0
