from reprise.formatters import simple_formatter
from tests.factories import reprisal_factory


class TestSimpleFormatter:
    def test_simple_formatter(self, session):
        reprisals = reprisal_factory(session=session).create_batch(2)
        result = simple_formatter(reprisals)

        motifs = [reprisal.motif for reprisal in reprisals]
        assert isinstance(result, str)
        assert result == f"{motifs[0].content}\n{motifs[1].content}"
