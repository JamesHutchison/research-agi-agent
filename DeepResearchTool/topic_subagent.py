import json
import logging

from langchain.utilities import GoogleSearchAPIWrapper
from superagi.helper.webpage_extractor import WebpageExtractor
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager

from DeepResearchTool.const import USER_QUERY_FILE
from DeepResearchTool.helpers import do_chat_and_log_it
from DeepResearchTool.topic_managers import Topic


class TopicSubAgent:
    def __init__(self, topic: Topic, file_manager: FileManager, llm: BaseLlm) -> None:
        self._topic = topic
        self._file_manager = file_manager
        self._llm = llm

    def _get_query_for_topic(self, user_query: str) -> str:
        query = (
            f"Given the topic: {self._topic.name} and the description: {self._topic.description} "
            "with the context that this topic came from the original user query: {user_query},"
            "come up with a single web search query to try to find information on the topic."
        )
        result = do_chat_and_log_it(self._llm, [{"role": "system", "content": query}])
        return result

    def _get_target_urls_for_results(self, search_results) -> list[str]:
        return [result["link"] for result in search_results]

    def do_research(self) -> str:
        user_query = self._file_manager.read_file(USER_QUERY_FILE)
        self.web_search(user_query)
        self.evaluate_next_steps()
        self._topic.mark_as_researched(self._file_manager)

    def web_search(self, user_query) -> None:
        search_query = self._get_query_for_topic(user_query)

        search = GoogleSearchAPIWrapper()
        # simple logic - top 3 results for now
        TOP_N_RESULTS = 3
        search_results = search.results(search_query, TOP_N_RESULTS)

        target_urls = self._get_target_urls_for_results(search_results)
        for url in target_urls:
            contents = self.scrape_web_page(url)
            notes = self.extract_notes(url, contents, user_query)
            self.update_notes_file(url, notes)
            subtopics = self.extract_subtopics(contents, user_query)
            self.maybe_add_subtopics(subtopics)

    def scrape_web_page(self, url: str) -> str:
        contents = WebpageExtractor().extract_with_bs4(url)
        contents = contents[:3000]
        return contents

    def extract_notes(self, url: str, contents: str, user_query: str) -> str:
        topic = self._topic
        relevant_because = topic.relevant_because

        query = (
            f"Given the topic: {topic.name} read through the following and take notes on the topic. "
            "The notes will identify facts about the topic. The facts and information about the topic "
            "should consider how it is revelant to the overall research. The overall research identified "
            f"that this topic was revelant because {relevant_because}. "
            "The notes need to be short and concise. Consider how it relates to the original user query: "
            f"{user_query}"
            "Consider how information may dispute claims in the user query. Consider conflicting information. "
            "Consider supporting information\n"
            f"### Contents to read through: {contents}  ### end contents to read through"
        )
        result = do_chat_and_log_it(self._llm, [{"role": "system", "content": query}])
        return result

    def extract_subtopics(self, contents: str, user_query: str) -> list[str]:
        topic = self._topic
        relevant_because = topic.relevant_because

        query = (
            f"Given the topic: {topic.name} read through the following and extract subtopics. "
            "Subtopics are topics that are more specific than the current topic. "
            "The subtopics should be related to the current topic and the overall research. "
            "The overall research identified "
            f"that this topic was revelant because {relevant_because}. "
            "The subtopics need to be short and concise. Consider how it relates to the original user query: "
            f"{user_query}."
            "\n\n The output format MUST be a JSON list of objects."
            """Provide a JSON list of these topics, each with a 'name', 'description', 'relevant_because', and 'file name' field.
No more than 5 major topics and prefer not creating any subtopics at all. The revelant_because field should be one or two sentences.
When creating topics, avoid specific permutations, subtopics, or detailed breakdowns. Each topic name should be self-explanatory
and understandable without additional context. If uncertain about a topic, leave the 'description' field empty.
For example, instead of 'Environmental Impact', use 'Fluoride's Environmental Consequences'."""
            f"### Contents to read through: {contents}  ### end contents to read through"
        )
        result = do_chat_and_log_it(self._llm, [{"role": "system", "content": query}])
        return json.loads(result)

    def maybe_add_subtopics(self, subtopics: list[str]) -> None:
        logging.warning("NOT IMPLEMENTED - Would possibly add subtopics {subtopics}")

    def update_notes_file(self, url: str, notes: str) -> None:
        notes_file = self._topic.notes_file
        incoming_notes = self._file_manager.read_file(notes_file)
        notes_file_contents: list[dict] = json.loads(incoming_notes)
        notes_file_contents.append({"url": url, "notes": notes})
        self._file_manager.write_file(notes_file, json.dumps(notes_file_contents))

    def evaluate_next_steps(self) -> None:
        pass  # not sure if anything to do here
