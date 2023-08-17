from abc import ABC
from typing import List, Type

from deep_research_tool import DeepResearchTool
from superagi.tools.base_tool import BaseTool, BaseToolkit


class DeepResearchToolkit(BaseToolkit, ABC):
    name: str = "Deep Research Toolkit"
    description: str = "Toolkit for doing deep research and writing summarized findings."

    def get_tools(self) -> List[BaseTool]:
        return [DeepResearchTool()]

    def get_env_keys(self) -> List[str]:
        return []
