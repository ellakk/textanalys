import xml.etree.ElementTree as ET
from typing import List


class Word:
    """Represents a word and its attributes based on information from Sparv.

    Check: https://spraakbanken.gu.se/swe/forskning/infrastruktur/sparv/annotationer
    For more informatin about what the attributes mean and additional ones that can be
    implemented.

    """

    def __init__(self, word_node: ET.Element) -> None:
        if not isinstance(word_node.text, str):
            raise Exception("Invalid word node used to initialize instance.")
        self.text: str = word_node.text
        self.wordclass: str = word_node.attrib["pos"]
        self.morphosyntax: str = word_node.attrib["msd"]
        self.attitude: str = word_node.attrib["sentimentclass"]
        self.dependency_relation: str = word_node.attrib["deprel"]
        self.reference: str = word_node.attrib["ref"]
        self.dependency_head: str = word_node.attrib["dephead"]
        self.baseform: List[str] = [
            w for w in word_node.attrib["lemma"].split("|") if w
        ]
