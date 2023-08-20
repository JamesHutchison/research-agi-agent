import json
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

        # user_query = self.resource_manager.read_file(USER_QUERY_FILE)
        # topics = self.resource_manager.read_file(TOPICS_FILE)

        with (SAMPLE_DIR / USER_QUERY_FILE).open("r") as f:
            user_query = f.read()

        with (SAMPLE_DIR / TOPICS_FILE).open("r") as f:
            topics = f.read()

        topics_str_list = []

        for topic in json.loads(topics):
            notes_file = SAMPLE_DIR / Path(topic["notes_file"])
            with notes_file.open("r") as f:
                notes = f.read()
            # format is:
            # name, description, notes_file, relevant_because, researched
            topic_str = f"""
Topic name: {topic["name"]}
Topic description: {topic["description"]}
Relevant because: {topic["relevant_because"]}
Notes: {notes}
        """
            topics_str_list.append(topic_str)

        markdown_prompt = f"""
        The user query is: {user_query}

        ###

        Given the following topics and notes about the topic, write an article addressing the user query
        the best you can. If there is an question, try to answer it. If the user query has incorrect
        facts or assumptions, address that.

        Start with a problem statement of some sort based on the user query, then follow up with a conclusion.
        After the conclusion, explain how that conclusion was derived from the
        topics researched. If needed, create a section for relevant topic, if it is important enough,
        and explain how the topic contributes to the conclusion. You do not need to specifically mention
        the conclusion when describing topics.

        When you can, cite your sources

        ### The topics are:

        {"    # next topic #   ".join(topics_str_list)}

        # Reminder! The conclusion should be helpful and specific. If there are upper and lower bounds or circumstances where something
        may be true or false, then define it. If you cannot, then identify further research needed to get there. Do not make anything up!
        If you do not know why you know something, then do not mention it, or identify further research needed to confirm it.

        Use inline citations.

        Markdown file contents:
        """
        logging.warning(markdown_prompt)

        # content = self.llm.chat_completion([{"role": "system", "content": markdown_prompt}])[
        #     "content"
        # ]

        system_message_prompt = SystemMessage(content=markdown_prompt)
        response = self.llm([system_message_prompt])
        content = response.content

        print(content)

        with SINGLE_FILE_OUTPUT_FILE.open("w") as f:
            f.write(content)

        return f"Deep research completed! Check the resource manager for {SINGLE_FILE_OUTPUT_FILE} to view the result!"


DeepResearchWriterTool()._execute("test")
