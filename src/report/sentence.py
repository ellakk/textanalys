import xml.etree.ElementTree as ET
from typing import List

from src.report.word import Word


class Sentence:
    """Represents a sentence from a report."""

    def __init__(self, sentence_node: ET.Element) -> None:
        self.words: List[Word] = []
        self.text: str = sentence_node.attrib["original"]

        for word_node in sentence_node:
            if word_node.tag == "w":
                self.words.append(Word(word_node))
            elif word_node.tag == "ne":  # named entity
                for word_ne in word_node:
                    self.words.append(Word(word_ne))
            else:
                raise Exception(f"Unreqognized tag {word_node.tag}")

    def has_word(self, word: Word) -> bool:
        return word in self.words
