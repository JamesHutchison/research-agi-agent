from typing import Type

from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool


class DeepResearch(BaseModel):
    user_query: str = Field(..., description="The user query")


class DeepResearchTool(BaseTool):
    """
    Tool for starting and managing deep research. This should be used prior to doing any other deep research tools.
    """

    name: str = "Deep Research Tool"
    args_schema: Type[BaseModel] = DeepResearch
    description: str = (
        "Starts and manages the progress of deep researching a user query."
        "Helps determine the next steps to take"
    )

    def _execute(self, user_query: str | None = None) -> str:
        return f"""
            You are a researcher doing in depth research on a user's query. The user query is:

            {user_query}

            You will be following an algorithm to fully investigate the user query.

            TODO: the rest

            However, since this is a test, you are done. Good job! Simply reply with "Done!"
        """
