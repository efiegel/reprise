from langchain.chains.base import Chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class InformationExtractionChain(Chain):
    model: ChatOpenAI

    @property
    def chain(self):
        system_message = """
        You are an expert at extracting the important takeaways, facts, and lessons from
        text. You do this so that the information can be distilled for later reference.
        This includes identifying the "why" behind the information, if appropriate. You
        will be given a section of text. Extract the important takeaways, facts, and 
        lessons, including the "why" as appropriate, and return only these things as a 
        list using exactly this delimeter: ,,,.
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
        return {"information": response.content.split(",,,")}
