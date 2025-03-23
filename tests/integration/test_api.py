import pytest
from flask import json

from reprise.db import Citation, Motif, database_session
from tests.factories import citation_factory, cloze_deletion_factory, motif_factory


class TestAPI:
    @pytest.fixture
    def motif(self, session):
        return motif_factory(session=session).create()

    @pytest.fixture
    def citation(self, session):
        return citation_factory(session=session).create()

    def test_get_motifs(self, session, client, motif):
        motif_2 = motif_factory(session=session).create()
        cloze_deletion = cloze_deletion_factory(session=session).create(motif=motif_2)

        response = client.get("/motifs")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert len(data["motifs"]) == 2
        assert data["motifs"][0]["content"] == motif.content
        assert data["motifs"][0]["cloze_deletions"] is None
        assert data["motifs"][1]["cloze_deletions"] == [
            {"uuid": cloze_deletion.uuid, "mask_tuples": cloze_deletion.mask_tuples}
        ]

    def test_add_motif_without_citation(self, client):
        response = client.post(
            "/motifs",
            data=json.dumps({"content": "New motif content"}),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["content"] == "New motif content"
        assert data["citation"] is None

        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=data["uuid"]).one_or_none()
            assert motif.content == "New motif content"

    def test_add_motif_with_citation(self, client):
        response = client.post(
            "/motifs",
            data=json.dumps(
                {"content": "New motif content", "citation": "New citation"}
            ),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["content"] == "New motif content"
        assert data["citation"] == "New citation"

        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=data["uuid"]).one_or_none()
            assert motif.content == "New motif content"
            assert motif.citation.title == "New citation"

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

    def test_update_motif_invalid_citation(self, client, motif):
        response = client.put(
            f"/motifs/{motif.uuid}",
            data=json.dumps({"content": "Updated content", "citation": "invalid!"}),
            content_type="application/json",
        )

        assert response.status_code == 404

        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=motif.uuid).one_or_none()
            assert motif.content != "Updated content"

    def test_delete_motif(self, client, motif):
        response = client.delete(f"/motifs/{motif.uuid}")

        assert response.status_code == 200
        assert json.loads(response.data)["message"] == "Motif deleted"

        with database_session() as session:
            assert len(session.query(Motif).filter_by(uuid=motif.uuid).all()) == 0

    def test_create_citation(self, client):
        response = client.post(
            "/citations",
            data=json.dumps({"title": "New citation title"}),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["title"] == "New citation title"

        with database_session() as session:
            citation = (
                session.query(Citation).filter_by(uuid=data["uuid"]).one_or_none()
            )
            assert citation.title == "New citation title"

    def test_get_citations(self, client, citation):
        response = client.get("/citations")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["title"] == citation.title

    def test_add_citation_to_motif(self, client, motif, citation):
        response = client.put(
            f"/motifs/{motif.uuid}",
            data=json.dumps({"content": motif.content, "citation": citation.title}),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["citation"] == citation.title

        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=motif.uuid).one_or_none()
            assert motif.citation.title == citation.title

    def test_reprise_motifs(self, session, client, motif):
        motif_2 = motif_factory(session=session).create()
        cloze_deletion = cloze_deletion_factory(session=session).create(motif=motif_2)

        response = client.post("/reprise")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert len(data) > 0
        assert data[0]["content"] == motif.content
        assert data[0]["cloze_deletions"] is None
        assert data[1]["cloze_deletions"] == [
            {"uuid": cloze_deletion.uuid, "mask_tuples": cloze_deletion.mask_tuples}
        ]

    def test_get_motifs_paginated(self, client, session):
        motif_factory(session=session).create_batch(12)

        # first page
        response = client.get("/motifs?page=1&page_size=5")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert len(data["motifs"]) == 5
        assert data["total_count"] == 12

        # second page
        response = client.get("/motifs?page=2&page_size=5")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert len(data["motifs"]) == 5

        # third page
        response = client.get("/motifs?page=3&page_size=5")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert len(data["motifs"]) == 2

        # empty page
        response = client.get("/motifs?page=4&page_size=5")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert len(data["motifs"]) == 0

    def test_add_cloze_deletion(self, client, motif):
        response = client.post(
            "/cloze_deletions",
            data=json.dumps(
                {"motif_uuid": motif.uuid, "mask_tuples": [[0, 2], [4, 6]]}
            ),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["mask_tuples"] == [[0, 2], [4, 6]]

        with database_session() as session:
            motif = session.query(Motif).filter_by(uuid=motif.uuid).one_or_none()
            assert len(motif.cloze_deletions) == 1
            assert motif.cloze_deletions[0].mask_tuples == [[0, 2], [4, 6]]

    def test_update_cloze_deletion(self, session, client, motif):
        cloze_deletion = cloze_deletion_factory(session=session).create(
            motif=motif, mask_tuples=[[0, 2]]
        )

        response = client.put(
            "/cloze_deletions",
            data=json.dumps(
                {"uuid": cloze_deletion.uuid, "mask_tuples": [[1, 3], [5, 7]]}
            ),
            content_type="application/json",
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["mask_tuples"] == [[1, 3], [5, 7]]

        with database_session() as session:
            updated_cloze_deletion = (
                session.query(Motif)
                .filter_by(uuid=motif.uuid)
                .one_or_none()
                .cloze_deletions[0]
            )
            assert updated_cloze_deletion.mask_tuples == [[1, 3], [5, 7]]

    def test_delete_cloze_deletion(self, session, client, motif):
        cloze_deletion = cloze_deletion_factory(session=session).create(
            motif=motif, mask_tuples=[[0, 2]]
        )

        response = client.delete(f"/cloze_deletions/{cloze_deletion.uuid}")
        assert response.status_code == 200
        assert json.loads(response.data)["message"] == "Cloze deletion deleted"

        with database_session() as session:
            assert (
                session.query(Motif)
                .filter_by(uuid=motif.uuid)
                .one_or_none()
                .cloze_deletions
                == []
            )
