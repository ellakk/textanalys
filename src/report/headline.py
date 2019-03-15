import xml.etree.ElementTree as ET
from typing import List

from src.report.sentence import Sentence


class Headline:
    """Represents a headline from a report."""

    def __init__(self, headline_node: ET.Element) -> None:
        self.name: str = headline_node.attrib["name"]
        self.sentences: List[Sentence] = []

        for sentence_node in headline_node:
            self.sentences.append(Sentence(sentence_node))

    def to_text(self) -> str:
        """Textual representation of the headline."""
        text: str = f"{self.name}\n"
        for sentence in self.sentences:
            text += sentence.text + " "
        return text.strip()
