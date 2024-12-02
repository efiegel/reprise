from langchain_openai import ChatOpenAI

from reprise.llm.chains import InformationExtractionChain
from tests.utils import patch_model_responses


class TestInformationExtractionChain:
    def test_information_extraction_chain(self):
        model = ChatOpenAI(model="gpt-4o-mini")
        chain = InformationExtractionChain(model=model)
        with patch_model_responses(["the sky is blue,,,grass is green"]):
            result = chain.invoke(
                {
                    "content": "doesn't matter - this is going to be mocked out",
                }
            )
        assert result["information"] == ["the sky is blue", "grass is green"]
