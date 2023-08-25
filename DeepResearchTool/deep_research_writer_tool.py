import json
import logging
from typing import Any, Optional, Type

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool

from DeepResearchTool.const import SINGLE_FILE_OUTPUT_FILE, TOPICS_FILE, USER_QUERY_FILE
from DeepResearchTool.deep_research.summary_generator import SummaryGenerator


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

    def _notes_getter(self, notes_file: str) -> str:
        assert self.resource_manager

        return self.resource_manager.read_file(notes_file)

    def _execute(self, desired_output_format: str | None = None) -> str:
        assert self.resource_manager
        assert self.llm

        self.llm.temperature = 0

        user_query, topics = self._read_files()

        summary_writer = SummaryGenerator(user_query, topics, self._notes_getter)
        content = summary_writer.get_markdown_summary()
        self.resource_manager.write_file(SINGLE_FILE_OUTPUT_FILE, content)

        return f"Deep research completed! Check the resource manager for {SINGLE_FILE_OUTPUT_FILE} to view the result!"
