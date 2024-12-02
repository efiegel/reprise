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
        list using exactly this delimeter: ,,,. Unless absolutely necessary for proper
        context, don't return anything else, such as bullets or step numbers. Break up
        these pieces of information into digestable sizes as necessary.

        Remember that each extracted takeaway needs to be intelligible on its own. For 
        example, if the sample of text is "let the flour absorb water for 10 minutes 
        before kneading, then knead the dough for 5 minutes, then let it rest for 10.
        All of this helps gluten develop properly." then an appropriate extraction would
        be "letting the flour absorb water helps gluten develop properly,,,kneading the
        dough helps gluten develop properly,,,resting the dough helps gluten develop
        properly,,,make dough by letting flour absorb water, kneading, and resting"
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
        pieces_of_information = response.content.split(",,,")
        return {"information": [info.strip() for info in pieces_of_information]}
