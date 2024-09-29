import textwrap

from reprise.motif import Motif


class TestMotif:
    def test_create_motif(self, tmp_path):
        content, citations = "Hello, World!", ["abc", 123]
        expected_file_contents = textwrap.dedent("""
        ---
        citations:
         - "[[abc]]"
         - "[[123]]"
        ---
        Hello, World!
        """).strip()

        motif = Motif(content, citations)
        motif.save(tmp_path)

        with open(f"{tmp_path}/{motif.uuid}.md") as file:
            assert file.read() == expected_file_contents

    def test_format_frontmatter(self):
        content, citations = "Hello, World!", ["abc", 123]
        expected_frontmatter = textwrap.dedent("""
        ---
        citations:
         - "[[abc]]"
         - "[[123]]"
        ---
        """).strip()

        motif = Motif(content, citations)
        assert motif._format_frontmatter() == expected_frontmatter

    def test_format_frontmatter_no_citations(self):
        content, citations = "Hello, World!", []
        expected_frontmatter = textwrap.dedent("""
        ---
        citations:
        ---
        """).strip()

        motif = Motif(content, citations)
        assert motif._format_frontmatter() == expected_frontmatter
