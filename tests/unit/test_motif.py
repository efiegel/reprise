from reprise.motif import Motif


class TestMotif:
    def test_create_motif(self, tmp_path):
        content = "Hello, World!"
        motif = Motif(content)
        motif.save(tmp_path)

        with open(f"{tmp_path}/{motif.uuid}.md") as file:
            assert file.read() == content
