import pytest
from flask import json

from reprise.db import Motif, database_session
from reprise.factories import motif_factory


class TestAPI:
    @pytest.fixture
    def motif(self, session):
        return motif_factory(session=session).create()

    def test_get_motifs(self, client, motif):
        response = client.get("/motifs")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["content"] == motif.content
        assert data[0]["citation"] == motif.citation

    def test_add_motif(self, client):
        response = client.post(
            "/motifs",
            data=json.dumps({"content": "New motif content"}),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["content"] == "New motif content"

        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=data["uuid"]).one_or_none()
            assert motif.content == "New motif content"

    def test_update_motif(self, client, motif):
        response = client.put(
            f"/motifs/{motif.uuid}",
            data=json.dumps({"content": "Updated content"}),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["content"] == "Updated content"

        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=motif.uuid).one_or_none()
            assert motif.content == "Updated content"

    def test_delete_motif(self, client, motif):
        response = client.delete(f"/motifs/{motif.uuid}")

        assert response.status_code == 200
        assert json.loads(response.data)["message"] == "Motif deleted"

        with database_session() as session:
            assert len(session.query(Motif).filter_by(uuid=motif.uuid).all()) == 0
