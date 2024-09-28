from reprise.vault import Vault


class TestVault:
    def test_add_motif(self, tmp_path, monkeypatch):
        monkeypatch.setenv("VAULT_DIRECTORY", tmp_path)
        content = "Hello, World!"
        vault = Vault()
        motif = vault.add_motif(content)

        with open(f"{tmp_path}/{motif.uuid}.md") as file:
            assert file.read() == content
