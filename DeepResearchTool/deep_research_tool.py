import json
import logging
from typing import Optional, Type

from pydantic import BaseModel, Field
from regex import F
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool

from DeepResearchTool.const import TOPICS_FILE, USER_QUERY_FILE
from DeepResearchTool.helpers import do_chat_and_log_it
from DeepResearchTool.topic_managers import Topic, TopicsManager


class DeepResearch(BaseModel):
    user_query: str = Field(
        ...,
        description="The user query. Only provide this the first time you use this tool. "
        "This should match exactly what the user provided.",
    )


class DeepResearchManagerTool(BaseTool):
    """
    Tool for starting and managing deep research. This should be used prior to doing any other deep research tools.
    """

    name: str = "Deep Research Tool"
    args_schema: Type[BaseModel] = DeepResearch
    description: str = (
        "Starts and manages the progress of deep researching a user query."
        "Helps determine the next steps to take. If you are stuck on what to do next "
        "while doing deep research, then use this tool."
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
The topic could be researched on the Internet.

Not Appropriate for Deep Extensive Research:

The topic is based on conspiracy theories, myths, or fictional characters.
The topic is written in a biased, sarcastic, or mocking tone.
The topic is too narrow or specific to warrant extensive research.
The topic is about a personal issue or problem.

Good example:
Write a research paper on how quantum computers are possible

Bad example:
Why is my light bulb flickering?
"""
                    "Reason through why the user query is appropriate. If is, state the reasons and reply with '!!!OK!!!' "
                    "Otherwise, reply with a short sentence what is wrong with the query."
                ),
            },
        ]
        result = do_chat_and_log_it(self.llm, chat_query)
        if "!!!OK!!!" in result:
            return None
        return result

    def _extract_topics_from_user_query(self, user_query: str) -> str:
        assert self.llm

        result = do_chat_and_log_it(
            self.llm,
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
                        """
Examine the following information and extract the broadest and most general research topics.
Provide a JSON list of these topics, each with a 'name', 'description', 'relevant_because', and 'notes_file' field.
No more than 5 major topics and prefer 2 or less. The revelant_because field should be one or two sentences.
When creating topics, avoid specific permutations, subtopics, or detailed breakdowns. Each topic name should be self-explanatory
and understandable without additional context. If uncertain about a topic, leave the 'description' field empty.
For example, instead of 'Environmental Impact', use 'Fluoride's Environmental Consequences'.
The 'name', 'description', 'relevant_because', and 'notes_file' fields are all required!
The notes_file value should be a file name, no spaces, with a .json extension."""
                        "If you don't know what something is, leave the description field as an empty string.\n\nJSON:\n"
                    ),
                },
            ],
        )
        return result

    def _first_time_ran(self, user_query: str, resource_manager: FileManager) -> str:
        # run user query validation tool to see if we should proceed
        if user_query_issues := self._user_query_issues(user_query):
            return (
                f"The provided user query is not a good fit for deep research. Reasons: {user_query_issues}. "
                "Recommending aborting this goal and considering it complete."
            )

        # get topics and write to a file
        topics_str: str = self._extract_topics_from_user_query(user_query)
        # TODO: possibly use LangChain to auto-fix
        topics: list[Topic] = [Topic(**t) for t in json.loads(topics_str)]

        # initialize knowledge graph
        # TODO

        TopicsManager(resource_manager).write_topics(topics)
        for topic in topics:
            topic.initialize_notes_file(resource_manager)

        resource_manager.write_file(USER_QUERY_FILE, user_query)

        return f"""
            The research topics are: {topics}

            The process for doing deep research is to investigate the topics, take notes,
            evaluate if there are any new topics uncovered to research, and iterate through
            all the topics. Afterwards, coherently come to a conclusion, then use the
            Deep Research Writer Tool to write the output.

            The next step is to pick a topic and use the Deep Research Investigator Tool with it.
        """

    def _get_next_topic(self, resource_manager: FileManager) -> str | None:
        topics = TopicsManager(resource_manager).load_topics()
        for topic in topics:
            if not topic.researched:
                return topic.name
        return None

    def _execute(self, user_query: str | None = None) -> str:
        assert self.resource_manager
        assert self.llm

        self.llm.temperature = 0

        if not self.resource_manager.get_files():
            assert user_query

            return self._first_time_ran(user_query, self.resource_manager)
        if (next_topic := self._get_next_topic(self.resource_manager)) is not None:
            return f"Use the Deep Research Investigator Tool with the topic: {next_topic}"
        return "All topics have been researched. Use the Deep Research Writer Tool to write the output."
