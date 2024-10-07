from langchain_openai import ChatOpenAI

from .chains import InformationExtractionChain


class Agent:
    def __init__(self, model_name: str):
        self.model = ChatOpenAI(model=model_name)

    def extract_information(self, content: str) -> list[str]:
        chain = InformationExtractionChain(model=self.model)
        response = chain.invoke({"content": content})
        return response.get("information")
