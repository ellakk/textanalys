import xml.etree.ElementTree as ET
from typing import List
from src.report.word import Word


class NamedEntity:
    """Represents a named entity, more information at:
    http://www.lrec-conf.org/proceedings/lrec2014/pdf/391_Paper.pdf
    """
    def __init__(self, named_entity_node: ET.Element):
        self.identity: str = named_entity_node.attrib["ex"]
        self.type: str = named_entity_node.attrib["type"]
        self.subtype: str = named_entity_node.attrib["subtype"]
        self.words: List[Word] = []

        for word_node in named_entity_node:
            self.words.append(Word(word_node))
