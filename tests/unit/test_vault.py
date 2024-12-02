from datetime import datetime
from unittest.mock import MagicMock, patch

from reprise.vault import Diff, Vault


class TestVault:
    def test_diff_iterator(self):
        committed_datetime = datetime(2023, 1, 1)
        file = "test_file.py"
        changes = "+added line\n-removed line"

        mock_commit = MagicMock()
        mock_commit.committed_datetime = committed_datetime

        mock_diff = MagicMock()
        mock_diff.diff.decode.return_value = changes
        mock_diff.b_path = file

        mock_repo = MagicMock()
        with patch("reprise.vault.Repo", return_value=mock_repo):
            mock_repo.iter_commits.return_value = [mock_commit]
            mock_commit.parents = [MagicMock()]
            mock_commit.parents[0].diff.return_value = [mock_diff]

            vault = Vault(directory="")
            diffs = list(vault.diff_iterator())

        assert diffs[0] == Diff(
            date=committed_datetime,
            file=file,
            changes=changes,
        )
