import re
import json
import xml.etree.ElementTree as ET
from functools import reduce
from typing import List, Tuple

from docx import Document
import requests

from src.report.headline import Headline
from src.report.word import Word


class Report:
    """Represents a report. It gets most of its attributes from the Sparv API that
    it calls during initialization.

    """

    def __init__(self, document: Document) -> None:
        self.document = document

        self.headlines = []
        root_node = self._sparv_get_analysis()
        text_node = root_node.find("corpus/text")
        for headline_node in text_node:
            self.headlines.append(Headline(headline_node))

        self.lix = float(text_node.attrib['lix'])
        self.ovix = float(text_node.attrib['ovix'])
        self.nk = float(text_node.attrib['nk'])

    def _sparv_convert_document_to_xml(self) -> str:
        """Convert the document to an XML object and return it as a string. This
        document is only useful when sent to the Sparv API with our custom
        configuration.
        """

        def split_and_keep_delimiter(s: str, sep: str) -> List[str]:
            return reduce(
                lambda acc, elem: acc[:-1] + [acc[-1] + elem]
                if elem == sep else acc + [elem],
                re.split("(%s)" % re.escape(sep), s),
                [],
            )

        root_node = ET.Element("text", attrib={"title": "Anmälan"})
        current_headline = None
        for paragraph in self.document.paragraphs:
            text = paragraph.text.strip()
            # Is it a headline or just text
            if re.match(r"(^\w+\s?\w+\s?\w+\s?$)", text):
                current_headline = ET.SubElement(
                    root_node, "paragraph", attrib={"name": text})
            elif current_headline is not None and text:
                # Split sentences
                for sentence in split_and_keep_delimiter(text, ". "):
                    if not sentence:
                        continue
                    elif sentence[-1] == " ":
                        sentence = sentence[:-1]
                    sentence_node = ET.SubElement(
                        current_headline,
                        "sentence",
                        attrib={"original": sentence})
                    sentence_node.text = sentence

        return ET.tostring(root_node, encoding="unicode")

    def _sparv_get_analysis(self) -> ET.Element:
        """Fetches analysis about the report from the Sparv API and returns it as an
        XML object.
        Current setting are hashed at:
        https://spraakbanken.gu.se/sparv/#advanced=false&hash=
        fccea59f54ed3a21859449b148368f9e4cb5f5af&input=xml&lang=sv&language=sv
        Change hash if updating settings variable."""
        settings = json.dumps({
            "corpus":
            "untitled",
            "lang":
            "sv",
            "textmode":
            "xml",
            "word_segmenter":
            "default_tokenizer",
            "sentence_segmentation": {
                "tag": "sentence",
                "attributes": ["original"]
            },
            "paragraph_segmentation": {
                "tag": "paragraph",
                "attributes": ["name"]
            },
            "root": {
                "tag": "text",
                "attributes": ["title"]
            },
            "extra_tags": [],
            "positional_attributes": {
                "lexical_attributes": ["pos", "msd", "lemma", "lex", "sense"],
                "compound_attributes": ["complemgram", "compwf"],
                "dependency_attributes": ["ref", "dephead", "deprel"],
                "sentiment": ["sentiment", "sentimentclass"],
            },
            "named_entity_recognition": ["ex", "type", "subtype"],
            "text_attributes": {
                "readability_metrics": ["lix", "ovix", "nk"]
            }
        })
        response = requests.get(
            "https://ws.spraakbanken.gu.se/ws/sparv/v2/",
            data={
                "text": self._sparv_convert_document_to_xml(),
                "mode": "xml",
                "settings": settings
            })
        if response.status_code == 200:
            sparv_data = response.text.strip()
            return ET.fromstring(sparv_data)

        raise Exception(
            f"Sparv returned unexpected code: {response.status_code}")

    def get_regex_position(self, regex) -> Tuple[int, int]:
        """Returns the start and end position of regex."""
        match = re.search(regex, self.to_text())
        if match:
            return match.span()
        return 0, 0

    def get_word_postion(self, word: Word) -> Tuple[int, int]:
        """Get start and end position of the word in the report."""
        text = self.to_text()
        words = self.get_words()
        current_position = 0

        for w in words:
            current_position = text.find(w.text, current_position)
            if w == word:
                return (current_position, current_position + len(w.text))
        return 0, 0

    def get_words(self) -> List[Word]:
        return [
            word for headline in self.headlines
            for sentence in headline.sentences for word in sentence.words
        ]

    def to_text(self) -> str:
        return "\n\n".join(
            [headline.to_text() for headline in self.headlines]).strip()
