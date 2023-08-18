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
        result = self.llm.chat_completion(
            [
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
                    "content": user_query,
                },
                {
                    "role": "system",
                    "content": (
                        "Determine if the user query is suitable for research. If is, reply with 'OK!'. "
                        "Otherwise, reply with a short sentence what is wrong with the query."
                    ),
                },
            ]
        )
        if result["content"] == "OK!":
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
                        "Do not exceed 10 topics. Be short and stick to only major items. Do not create permutations and subtopics."
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
                return f"The provided user query is not a good fit for research. Reasons: {user_query_issues}"

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
