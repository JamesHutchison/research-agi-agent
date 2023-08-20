import json
import logging
from typing import Optional, Type

from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool

from DeepResearchTool.const import TOPICS_FILE, USER_QUERY_FILE


class DeepResearch(BaseModel):
    user_query: str = Field(
        ..., description="The user query. Only provide this the first time you use this tool."
    )


class DeepResearchManagerTool(BaseTool):
    """
    Tool for starting and managing deep research. This should be used prior to doing any other deep research tools.
    """

    name: str = "Deep Research Tool"
    args_schema: Type[BaseModel] = DeepResearch
    description: str = (
        "Starts and manages the progress of deep researching a user query."
        "Helps determine the next steps to take"
    )
    llm: Optional[BaseLlm] = None
    resource_manager: Optional[FileManager] = None

    def _user_query_issues(self, user_query: str | None = None) -> str | None:
        assert self.llm

        if user_query is None:
            return "A user query was not provided and is required"
        query_issues_instructions = "Determine whether the user query is a good fit for research."
        chat_query = [
            {
                "role": "system",
                "content": " ".join(
                    [
                        "You are a research tool, and will be researching this user query.",
                        query_issues_instructions,
                    ]
                ),
            },
            {
                "role": "user",
                "content": "user query: " + user_query,
            },
            {
                "role": "system",
                "content": (
                    """
Use the following rules to determine if a user query previously given is appropriate for research:

The topic is based on scientific, economic, or sociological principles.
The topic is not based on conspiracy theories or unproven myths.
The topic is not biased or written in a sarcastic or mocking tone.
The topic is broad enough to warrant extensive research.
Not Appropriate for Deep Extensive Research:

The topic is based on conspiracy theories, myths, or fictional characters.
The topic is written in a biased, sarcastic, or mocking tone.
The topic is too narrow or specific to warrant extensive research.
"""
                    "Reason through why the user query is appropriate. If is, state the reasons and reply with '!!!OK!!!' "
                    "Otherwise, reply with a short sentence what is wrong with the query."
                ),
            },
        ]
        result = self.llm.chat_completion(chat_query)
        logging.warning(json.dumps(chat_query))
        logging.warning(result["content"])
        if "!!!OK!!!" in result["content"]:
            return None
        return result["content"]

    def _extract_topics_from_user_query(self, user_query: str) -> str:
        assert self.llm

        result = self.llm.chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a research tool. "
                        "Examine the following information and extract the relevant topics of research."
                    ),
                },
                {
                    "role": "user",
                    "content": user_query,
                },
                {
                    "role": "system",
                    "content": (
                        "Return a json list of topics, containing a 'name' field and a 'description' field. "
                        """
Examine the following information and extract the broadest and most general research topics.
Provide a JSON list of these topics, each with a 'name' and a 'description' field. Limit to 5 major topics.
Avoid specific permutations, subtopics, or detailed breakdowns. Each topic name should be self-explanatory
and understandable without additional context. If uncertain about a topic, leave the 'description' field empty.
For example, instead of 'Environmental Impact', use 'Fluoride's Environmental Consequences'. """
                        "If you don't know what something is, leave the description field as an empty string."
                    ),
                },
            ]
        )
        return result["content"]

    def _execute(self, user_query: str | None = None) -> str:
        assert self.resource_manager
        assert self.llm

        self.llm.temperature = 0

        if not self.resource_manager.get_files():
            # first time being ran

            # run user query validation tool to see if we should proceed
            if user_query_issues := self._user_query_issues(user_query):
                return f"The provided user query is not a good fit for deep research. Reasons: {user_query_issues}"

            assert user_query

            # get topics and write to a file
            topics: str = self._extract_topics_from_user_query(user_query)
            # TODO: possibly use LangChain to auto-fix

            # initialize knowledge graph
            # TODO

            self.resource_manager.write_file(TOPICS_FILE, topics)
            self.resource_manager.write_file(USER_QUERY_FILE, user_query)

            return f"""
                The research topics are: {topics}

                The next step is to use the DeepResearchWriterTool to write a blurb on the topics to research.
                You MUST use the DeepResearchWriterTool next. The argument it will take is 'test'.
            """
        return "Oops, use the DeepResearchWriterTool next."
