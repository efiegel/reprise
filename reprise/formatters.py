from reprise.db import Reprisal


def simple_formatter(reprisals: list[Reprisal]) -> str:
    return "\n".join([reprisal.motif.content for reprisal in reprisals])
