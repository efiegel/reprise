import pytest

from reprise.vault import Vault


class TestVault:
    @pytest.fixture(autouse=True)
    def motif_directory(self, tmp_path):
        dir = tmp_path / ".motifs"
        dir.mkdir()
        return dir

    def test_add_motif(self, tmp_path, motif_directory):
        vault = Vault(tmp_path)

        content = "Hello, World!"
        motif = vault.add_motif(content)
        with open(f"{motif_directory}/{motif.uuid}.md") as file:
            assert file.read() == content
