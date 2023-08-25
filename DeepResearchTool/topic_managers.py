import json
import logging
from dataclasses import asdict

from superagi.resource_manager.file_manager import FileManager

from DeepResearchTool.const import TOPICS_FILE
from DeepResearchTool.deep_research.topics import Topic


class ManagedTopic:
    def __init__(self, topic: Topic, file_manager: FileManager) -> None:
        self.topic = topic
        self.file_manager = file_manager

    def initialize_notes_file(self) -> None:
        logging.info(f"Initializing notes file: {self.topic.notes_file}")
        self.file_manager.write_file(self.topic.notes_file, json.dumps([]))

    def mark_as_researched(self) -> None:
        topics_file = json.loads(self.file_manager.read_file(TOPICS_FILE))
        for topic in topics_file:
            if topic["name"] == self.topic.name:
                topic["researched"] = True
                break
        self.file_manager.write_file(TOPICS_FILE, json.dumps(topics_file))


class TopicsManager:
    def __init__(self, file_manager: FileManager) -> None:
        self._file_manager = file_manager

    def load_topics(self) -> list[ManagedTopic]:
        return [
            ManagedTopic(Topic(**topic), self._file_manager)
            for topic in json.loads(self._file_manager.read_file(TOPICS_FILE))
        ]

    def write_topics(self, topics: list[ManagedTopic]) -> None:
        writing_topics = [topic.topic for topic in topics]
        self._file_manager.write_file(
            TOPICS_FILE, json.dumps([asdict(topic) for topic in writing_topics])
        )
