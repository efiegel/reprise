from reprise.db import Motif, database_session


def test_database_session_rollback_on_exception():
    try:
        with database_session() as session:
            motif = Motif(content="test")
            session.add(motif)
            session.flush()
            raise Exception
    except Exception:
        pass

    with database_session() as session:
        assert session.query(Motif).count() == 0
