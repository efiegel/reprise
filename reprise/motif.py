from uuid import uuid4


class Motif:
    def __init__(self, content: str):
        self.content = content
        self.uuid = uuid4()

    def _format_obsidian_file(self):
        return self.content

    def save(self, directory: str):
        file_path = f"{directory}/{self.uuid}.md"
        with open(file_path, "w") as file:
            file_content = self._format_obsidian_file()
            file.write(file_content)
