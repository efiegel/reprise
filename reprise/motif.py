from uuid import uuid4


class Motif:
    def __init__(self, content: str, citations: list):
        self.content = content
        self.citations = citations
        self.uuid = uuid4()

    def _format_obsidian_file(self):
        frontmatter = self._format_frontmatter()
        return f"{frontmatter}\n{self.content}"

    def _format_frontmatter(self):
        frontmatter = "---\ncitations:\n"
        for citation in self.citations:
            frontmatter += f' - "[[{citation}]]"\n'
        frontmatter += "---"
        return frontmatter

    def save(self, directory: str):
        file_path = f"{directory}/{self.uuid}.md"
        with open(file_path, "w") as file:
            file_content = self._format_obsidian_file()
            file.write(file_content)
