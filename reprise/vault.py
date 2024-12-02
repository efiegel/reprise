from dataclasses import dataclass
from typing import Iterator

from git import NULL_TREE, Commit, Repo


@dataclass
class Diff:
    date: str
    file: str
    changes: str


class Vault:
    def __init__(self, directory: str):
        self.directory = directory

    def diff_iterator(self) -> Iterator[Diff]:
        for commit in self._get_commits():
            for diff in self._get_diffs(commit):
                commit_date = commit.committed_datetime
                yield self._convert_raw_diff_to_dataclass(commit_date, diff)

    def _get_commits(self) -> list[Commit]:
        repo = Repo(self.directory)
        return list(repo.iter_commits(rev="main"))

    def _get_diffs(self, commit: Commit):
        parent = commit.parents[0] if commit.parents else None
        if parent:
            diffs = parent.diff(commit, create_patch=True)
        else:
            diffs = commit.diff(NULL_TREE, create_patch=True)

        return diffs

    def _convert_raw_diff_to_dataclass(self, commit_date, diff) -> Diff:
        diff_text = diff.diff.decode("utf-8")

        changes = []
        for line in diff_text.splitlines():
            if line.startswith("+") or line.startswith("-"):
                changes.append(line)

        change_str = "\n".join(line for line in changes)
        return Diff(date=commit_date, file=diff.b_path, changes=change_str)
