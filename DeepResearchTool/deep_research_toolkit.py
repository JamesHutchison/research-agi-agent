from abc import ABC
from superagi.tools.base_tool import BaseToolkit, BaseTool
from typing import Type, List
from greetings_tool import GreetingsTool


class DeepResearchToolkit(BaseToolkit, ABC):
    name: str = "Deep Research Toolkit"
    description: str = "Toolkit for doing deep research and writing summarized findings."

    def get_tools(self) -> List[BaseTool]:
        return [GreetingsTool()]

    def get_env_keys(self) -> List[str]:
        return []
