from unittest.mock import MagicMock

import pytest

from reprise.llm import Agent
from tests.utils import patch_model_responses


class TestAgent:
    @pytest.fixture()
    def agent(self):
        return Agent(model_name="gpt-4o-mini")

    def test_extract_information(self, agent):
        with patch_model_responses(["the sky is blue, grass is green"]):
            assert agent.extract_information(MagicMock()) == [
                "the sky is blue",
                "grass is green",
            ]
