import json
import logging
from typing import Optional, Type

from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool

from DeepResearchTool.const import TOPICS_FILE
from DeepResearchTool.topic_managers import Topic, TopicsManager
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

    def _validate_topic(self, topic: str, topics: list[Topic]) -> str | None:
        assert self.resource_manager

        for t in topics:
            if t.name == topic:
                if t.researched:
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
        try:
            assert self.resource_manager

            tm = TopicsManager(self.resource_manager)

            topics = tm.load_topics()
            if (err_msg := self._validate_topic(topic, topics)) is not None:
                return err_msg

            for topic_obj in topics:
                if topic_obj.name == topic:
                    TopicSubAgent(topic_obj, self.resource_manager, self.llm).do_research()

                    # reload topics and determine if still some remaining
                    topics = tm.load_topics()

                    return_str = f"Deep research completed for topic {topic}! Do not research {topic} again!"
                    for potential_next_topic in topics:
                        if not potential_next_topic.researched:
                            return_str += (
                                "\n\nNew topics to research may have been created! "
                                f"Next topic to research: {potential_next_topic.name}"
                            )
                            break
                    return return_str
            raise Exception("Should not be here! Topic validation failed!")
        except Exception as e:
            logging.exception("")
            raise
