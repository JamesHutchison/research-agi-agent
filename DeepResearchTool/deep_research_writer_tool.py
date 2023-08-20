import json
import logging
from typing import Optional, Type

from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool

from DeepResearchTool.const import SINGLE_FILE_OUTPUT_FILE, TOPICS_FILE, USER_QUERY_FILE


class DeepResearchWriter(BaseModel):
    desired_output_format: str = Field(
        ...,
        description="The desired output format. The only valid value at this time is 'single_file'",
    )


class DeepResearchWriterTool(BaseTool):
    """
    Tool for writing the output of the Deep research tool. If deep research was not done, this tool will fail to run
    """

    name: str = "Deep Research Writer Tool"
    args_schema: Type[BaseModel] = DeepResearchWriter
    description: str = "Takes the results of the deep research and writes the output format"
    llm: Optional[BaseLlm] = None
    resource_manager: Optional[FileManager] = None

    def _execute(self, desired_output_format: str | None = None) -> str:
        assert self.resource_manager
        assert self.llm

        self.llm.temperature = 0

        user_query = self.resource_manager.read_file(USER_QUERY_FILE)
        topics = self.resource_manager.read_file(TOPICS_FILE)

        topics_str_list = []

        for topic in json.loads(topics):
            notes = self.resource_manager.read_file(topic["notes_file"])
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

        content = self.llm.chat_completion([{"role": "system", "content": markdown_prompt}])[
            "content"
        ]

        self.resource_manager.write_file(SINGLE_FILE_OUTPUT_FILE, content)

        return f"Deep research completed! Check the resource manager for {SINGLE_FILE_OUTPUT_FILE} to view the result!"
