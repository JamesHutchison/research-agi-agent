import logging
from typing import Callable, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage


class SummaryGenerator:
    _user_query: str
    _topics: list[dict]
    _notes_getter: Callable[[str], str]
    _chat: Callable[[str], str]

    def __init__(
        self,
        user_query: str,
        topics: list[dict],
        notes_getter: Callable[[str], str],
        chat: Optional[Callable[[str], str]] = None,
    ) -> None:
        self._user_query = user_query
        self._topics = topics
        self._notes_getter = notes_getter
        self._chat = chat or self._get_response_from_openai

    def _format_topic(self, topic: dict) -> str:
        notes = self._notes_getter(topic["notes_file"])
        topic_str = f"""
            Topic name: {topic["name"]}
            Topic description: {topic["description"]}
            Relevant because: {topic["relevant_because"]}
            Notes: {notes}
        """
        return topic_str

    def _generate_markdown_prompt(self, user_query: str, topics: list[dict]) -> str:
        topics_str_list = [self._format_topic(topic) for topic in topics]
        markdown_prompt = f"""
            The user query is: {user_query}

            ###

            Given the following topics and notes about the topic, write an article addressing the user query
            the best you can. If there is a question, try to answer it. If the user query has incorrect
            facts or assumptions, address that.

            Start with a problem statement of some sort based on the user query, then follow up with a conclusion.
            After the conclusion, explain how that conclusion was derived from the
            topics researched. If needed, create a section for relevant topic, if it is important enough,
            and explain how the topic contributes to the conclusion. You do not need to specifically mention
            the conclusion when describing topics.

            When you can, cite your sources

            ### The topics are:

            {"    # next topic #   ".join(topics_str_list)}

            # Reminder! The conclusion should be helpful and specific. If there are upper and lower bounds or circumstances where something
            may be true or false, then define it. If you cannot, then identify further research needed to get there. Do not make anything up!
            If you do not know why you know something, then do not mention it, or identify further research needed to confirm it.

            Use inline citations.

            Markdown file contents:
        """
        return markdown_prompt

    def get_markdown_summary(self) -> str:
        markdown_prompt = self._generate_markdown_prompt(self._user_query, self._topics)
        logging.warning(markdown_prompt)
        return self._chat(markdown_prompt)

    def _get_response_from_openai(self, markdown_prompt: str) -> str:
        OPEN_AI_MODEL = "gpt-4"
        chat = ChatOpenAI(model=OPEN_AI_MODEL, temperature=0)
        system_message_prompt = SystemMessage(content=markdown_prompt)
        response = chat([system_message_prompt])
        return response.content
