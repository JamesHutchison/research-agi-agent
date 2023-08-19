import json
from dataclasses import asdict, dataclass

from superagi.resource_manager.file_manager import FileManager

from DeepResearchTool.const import TOPICS_FILE


@dataclass
class Topic:
    name: str
    description: str
    notes_file: str
    relevant_because: str
    researched: bool = False

    def initialize_notes_file(self, file_manager: FileManager) -> None:
        file_manager.write_file(self.notes_file, json.dumps([]))

    def mark_as_researched(self, file_manager: FileManager) -> None:
        topics_file = json.loads(file_manager.read_file(TOPICS_FILE))
        for topic in topics_file:
            if topic["name"] == self.name:
                topic["researched"] = True
                break
        file_manager.write_file(TOPICS_FILE, json.dumps(topics_file))


class TopicsManager:
    def __init__(self, file_manager: FileManager) -> None:
        self._file_manager = file_manager

    def load_topics(self) -> list[Topic]:
        return [Topic(**topic) for topic in json.loads(self._file_manager.read_file(TOPICS_FILE))]

    def write_topics(self, topics: list[Topic]) -> None:
        self._file_manager.write_file(
            TOPICS_FILE, json.dumps([asdict(topic) for topic in topics])
        )
