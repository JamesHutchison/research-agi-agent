import json
from typing import Optional, Type

from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool

from DeepResearchTool.const import TOPICS_FILE
from DeepResearchTool.topic_managers import Topic
from DeepResearchTool.topic_subagent import TopicSubAgent


class DeepResearchInvestigator(BaseModel):
    topic: str = Field(..., description="The name of the topic. This must match exactly.")


class DeepResearchInvestigatorTool(BaseTool):
    """
    Tool for doing deep research on a topic. It may create more topics to research.
    """

    name: str = "Deep Research Investigator Tool"
    args_schema: Type[BaseModel] = DeepResearchInvestigator
    description: str = (
        "Tool to research a topic by searching the internet, taking notes, and identifying possible "
        "other topics. This tool will complete the research for this topic."
    )
    llm: Optional[BaseLlm] = None
    resource_manager: Optional[FileManager] = None

    def _validate_topic(self, topic: str, topics: list[dict]) -> str | None:
        assert self.resource_manager

        for t in topics:
            if t["name"] == topic:
                if t.get("researched", False):
                    return (
                        f"Topic {topic} has already been researched. "
                        "Use the Deep Research Tool for guidance on what to do next."
                    )
                return None
        return (
            f"Topic {topic} was not found. Be sure to name the topic exactly as it was given and "
            "use the Deep Research Tool to find the next topic."
        )

    def _execute(self, topic: str) -> str:
        assert self.resource_manager

        topics = json.loads(self.resource_manager.read_file(TOPICS_FILE))
        if (err_msg := self._validate_topic(topic, topics)) is not None:
            return err_msg

        for topic_obj in topics:
            if topic_obj["name"] == topic:
                TopicSubAgent(Topic(**topic_obj), self.resource_manager, self.llm).do_research()

                return f"Deep research completed for topic {topic}!"
        raise Exception("Should not be here! Topic validation failed!")
