import xml.etree.ElementTree as ET
from typing import List, Optional

from src.report.sentence import Sentence
from src.report.named_entity import NamedEntity


class Headline:
    """Represents a headline from a report."""

    def __init__(self, headline_node: ET.Element) -> None:
        self.name: str = headline_node.attrib["name"]
        self.sentences: List[Sentence] = []

        for sentence_node in headline_node:
            self.sentences.append(Sentence(sentence_node))

    def get_named_entities(
        self,
        identity: Optional[str] = None,
        type: Optional[str] = None,
        subtype: Optional[str] = None,
    ) -> List[NamedEntity]:
        """Returns a list of named entities from the text under the headline that matches the
        specifications."""
        found: List[NamedEntity] = []
        for named_entity in [e for s in self.sentences for e in s.named_entities]:
            if identity and (identity != named_entity.identity):
                continue
            if type and (type != named_entity.type):
                continue
            if subtype and (subtype != named_entity.subtype):
                continue
            found.append(named_entity)
        return found

    def has_named_entity(
        self, identity: str, type: Optional[str] = None, subtype: Optional[str] = None
    ) -> bool:
        """If the specified entity exists in the text under the headline."""
        if len(self.get_named_entities(identity, type, subtype)) > 0:
            return True
        return False

    def to_text(self) -> str:
        """Textual representation of the headline."""
        text: str = f"{self.name}\n"
        for sentence in self.sentences:
            text += sentence.text + " "
        return text.strip()
