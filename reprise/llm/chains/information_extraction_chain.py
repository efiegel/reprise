from langchain.chains.base import Chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class InformationExtractionChain(Chain):
    model: ChatOpenAI

    @property
    def chain(self):
        system_message = """
        You are an expert at comprehending documents and extracting the most important
        pieces of information from them. You will be given a section of text and must 
        return a list of the most important pieces of information from the text. Return
        the pieces of information just as a string, separated by commas.
        """

        template = """
        {system_message}
        {content}
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["content"],
            partial_variables={"system_message": system_message},
        )

        return prompt | self.model

    @property
    def input_keys(self) -> list[str]:
        return ["content"]

    @property
    def output_keys(self) -> list[str]:
        return ["information"]

    def _call(self, inputs):
        response = self.chain.invoke(inputs)
        return {"information": response.content}
