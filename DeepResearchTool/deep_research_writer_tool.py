from typing import Optional, Type

from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool

from DeepResearchTool.const import TOPICS_FILE, USER_QUERY_FILE


class DeepResearchWriter(BaseModel):
    desired_output_format: str = Field(
        ..., description="The desired output format. The only valid value at this time is 'test'"
    )


class DeepResearchWriterTool(BaseTool):
    """
    Tool for starting and managing deep research. This should be used prior to doing any other deep research tools.
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

        markdown_prompt = f"""
        The user query is: {user_query}

        ###

        The topics are: {topics}

        ###

        Provide a markdown formatted file describing the topics derived from the user query.

        Markdown file contents:
        """

        return (
            self.llm.chat_completion([{"role": "system", "content": markdown_prompt}])
            + "\nYou are done!"
        )
