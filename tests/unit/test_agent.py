from unittest.mock import patch

import pytest

from reprise.agent import (
    ClozeDeletionResult,
    find_word_indices,
    generate_cloze_deletions,
)


class TestAgent:
    @pytest.mark.parametrize(
        "text, words_to_mask, expected_indices",
        [
            ("The sky is blue", ["blue"], [[11, 14]]),
            (
                "The sky is blue and the grass is green",
                ["sky", "green"],
                [[4, 6], [33, 37]],
            ),
            ("The blue sky is blue", ["blue"], [[4, 7], [16, 19]]),
            ("The Sky is blue", ["Sky"], [[4, 6]]),
            ("The sky is blue", ["red"], []),
            ("The sky is blue", [], []),
            ("", ["word"], []),
            ("skylark skies sky", ["sky"], [[14, 16]]),
            ("The sky is blue and the blue sky is nice", ["blue sky"], [[24, 31]]),
            ("The problem: sky is very blue.", ["sky", "blue"], [[13, 15], [25, 28]]),
            ("The time complexity is O(n log n)", ["O(n log n)"], [[23, 32]]),
        ],
    )
    def test_find_word_indices_parametrized(
        self, text, words_to_mask, expected_indices
    ):
        """Test find_word_indices with various inputs using parametrization."""
        result = find_word_indices(text, words_to_mask)
        assert result == expected_indices

    @patch("pydantic_ai.agent.Agent.run_sync")
    def test_generate_cloze_deletions(self, mock_agent_run_sync):
        mock_agent_run_sync.return_value = ClozeDeletionResult(
            cloze_deletion_sets=[["sky", "blue"], ["is"]]
        )

        result = generate_cloze_deletions("The sky is blue")

        assert len(result) == 2
        assert result[0] == [[4, 6], [11, 14]]
        assert result[1] == [[8, 9]]

    @patch("pydantic_ai.agent.Agent.run_sync")
    def test_generate_cloze_deletions_with_n_max(self, mock_agent_run_sync):
        """Test the generate_cloze_deletions function with the n_max parameter."""
        mock_agent_run_sync.return_value = ClozeDeletionResult(
            cloze_deletion_sets=[["sky"], ["blue"], ["is"]]
        )

        result = generate_cloze_deletions("The sky is blue", n_max=5)

        # Verify the result has 3 sets (the model decided to use fewer than n_max)
        assert len(result) == 3
        assert result[0] == [[4, 6]]
        assert result[1] == [[11, 14]]
        assert result[2] == [[8, 9]]

    @patch("pydantic_ai.agent.Agent.run_sync")
    def test_generate_cloze_deletions_invalid_response(self, mock_agent_run_sync):
        mock_agent_run_sync.return_value = ClozeDeletionResult(
            cloze_deletion_sets=[["apples"]]
        )

        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "Invalid cloze deletion generation" in str(excinfo.value)
