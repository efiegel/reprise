from reprise.vault import Vault


class TestVault:
    def test_add_motif(self, tmp_path):
        vault = Vault(tmp_path)

        content = "Hello, World!"
        motif = vault.add_motif(content)
        with open(f"{tmp_path}/{motif.uuid}.md") as file:
            assert file.read() == content
