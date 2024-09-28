import os
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv()


class Motif:
    PERSISTENCE_DIR = f"{os.path.expanduser(os.getenv('VAULT_DIRECTORY'))}/.motifs"

    def __init__(self, content: str):
        self.content = content
        self.uuid = uuid4()

    def _format_obsidian_file(self):
        return self.content

    def save(self):
        file_path = f"{self.PERSISTENCE_DIR}/{self.uuid}.md"
        with open(file_path, "w") as file:
            file_content = self._format_obsidian_file()
            file.write(file_content)
