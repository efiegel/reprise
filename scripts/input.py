from reprise.db import database_context
from reprise.llm import Agent
from reprise.repository import add_motif

if __name__ == "__main__":
    text = input("enter some text: ")
    agent = Agent(model_name="gpt-4o-mini")
    with database_context():
        snippets = agent.extract_information(text)
        for snippet in snippets:
            add_motif(snippet, None)
