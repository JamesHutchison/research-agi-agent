import logging
from pathlib import Path
from typing import Optional, Type

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

OPEN_AI_MODEL = "gpt-3.5-turbo"
OPEN_AI_MODEL = "gpt-4"


class DeepResearchWriter(BaseModel):
    desired_output_format: str = Field(
        ...,
        description="The desired output format. The only valid value at this time is 'single_file'",
    )


class DeepResearchWriterTool:
    """
    Tool for writing the output of the Deep research tool. If deep research was not done, this tool will fail to run
    """

    name: str = "Deep Research Writer Tool"
    args_schema: Type[BaseModel] = DeepResearchWriter
    description: str = "Takes the results of the deep research and writes the output format"

    def __init__(self):
        self.llm = ChatOpenAI(model=OPEN_AI_MODEL, temperature=0)

    def _execute(self, desired_output_format: str | None = None) -> str:
        SAMPLE_DIR = Path("sample_output")

        USER_QUERY_FILE = Path("user_query.txt")
        TOPICS_FILE = Path("topics.json")
        SINGLE_FILE_OUTPUT_FILE = Path("SUMMARY_DEBUG_OUTPUT.md")
        assert self.llm

        self.llm.temperature = 0

        with (SAMPLE_DIR / USER_QUERY_FILE).open("r") as f:
            user_query = f.read()

        with (SAMPLE_DIR / TOPICS_FILE).open("r") as f:
            topics = f.read()

        markdown_prompt = f"""
        The user query is: {user_query}

        ###

        The topics are: {topics}

        ###

        Provide a markdown formatted file describing the topics derived from the user query.

        Markdown file contents:
        """
        logging.warning(markdown_prompt)

        # content = self.llm.chat_completion([{"role": "system", "content": markdown_prompt}])[
        #     "content"
        # ]

        system_message_prompt = SystemMessage(content=markdown_prompt)
        response = self.llm([system_message_prompt])
        content = response.content

        # chain = LLMChain(llm=self.llm, prompt=PromptTemplate.from_template(markdown_prompt))
        # content = chain.run(markdown_prompt)

        print(content)

        with SINGLE_FILE_OUTPUT_FILE.open("w") as f:
            f.write(content)

        return f"Deep research completed! Check the resource manager for {SINGLE_FILE_OUTPUT_FILE} to view the result!"


DeepResearchWriterTool()._execute("test")
