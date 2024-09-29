import textwrap

import pytest

from reprise.vault import Vault


class TestVault:
    @pytest.fixture(autouse=True)
    def motif_directory(self, tmp_path):
        dir = tmp_path / "motifs"
        dir.mkdir()
        return dir

    def test_add_motif(self, tmp_path, motif_directory):
        content, citations = "Hello, World!", ["abc", 123]
        expected_file_contents = textwrap.dedent(f"""
        ---
        citations:
         - "[[abc]]"
         - "[[123]]"
        ---
        {content}
        """).strip()

        vault = Vault(tmp_path)
        motif = vault.add_motif(content, citations)
        with open(f"{motif_directory}/{motif.uuid}.md") as file:
            assert file.read() == expected_file_contents
