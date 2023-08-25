from dataclasses import dataclass


@dataclass
class Topic:
    name: str
    description: str
    notes_file: str
    relevant_because: str
    researched: bool = False
