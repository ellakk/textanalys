import tempfile
import subprocess
import json
import re
import xml.etree.ElementTree as ET
from functools import reduce
from typing import List, Match, Optional, Tuple, Dict, IO, Any, Iterator

import requests
from docx import Document

from src.report.headline import Headline
from src.report.word import Word


class Report:
    """Represents a report. It gets most of its attributes from the Sparv API that
    it calls during initialization.

    """

    def __init__(self, document: Document) -> None:
        self.document: Document = document

        self.headlines: List[Headline] = []
        root_node: ET.Element = self._sparv_get_analysis()
        text_node: Optional[ET.Element] = root_node.find("corpus/text")
        if not text_node:
            return
            # raise Exception("Could not find corpus/text node")

        for headline_node in text_node:
            self.headlines.append(Headline(headline_node))

        self.lix: float = float(text_node.attrib["lix"])
        self.ovix: float = float(text_node.attrib["ovix"])
        self.nk: float = float(text_node.attrib["nk"])

    def _sparv_convert_document_to_xml(self) -> str:
        """Convert the document to an XML object and return it as a string. This
        document is only useful when sent to the Sparv API with our custom
        configuration.
        """

        def split_and_keep_delimiter(s: str, sep: str) -> List[str]:
            return reduce(
                lambda acc, elem: acc[:-1] + [acc[-1] + elem]
                if elem == sep
                else acc + [elem],
                re.split("(%s)" % re.escape(sep), s),
                [],
            )

        root_node = ET.Element("text", attrib={"title": "Anmälan"})
        current_headline: Optional[ET.Element] = None
        for paragraph in self.document.paragraphs:
            text: str = paragraph.text.strip()
            # Is it a headline or just text
            if re.match(r"(^\w+\s?\w+\s?\w+\s?\:?$)", text) and text.isupper():
                current_headline = ET.SubElement(
                    root_node, "paragraph", attrib={"name": text}
                )
            elif current_headline is not None and text:
                # Split sentences
                for sentence in split_and_keep_delimiter(text, ". "):
                    if not sentence:
                        continue
                    elif sentence[-1] == " ":
                        sentence = sentence[:-1]
                    sentence_node = ET.SubElement(
                        current_headline, "sentence", attrib={"original": sentence}
                    )
                    sentence_node.text = sentence

        return ET.tostring(root_node, encoding="unicode")

    def _sparv_get_analysis(self) -> ET.Element:
        """Fetches analysis about the report from the Sparv API and returns it as an
        XML object.
        Current setting are hashed at:
        https://spraakbanken.gu.se/sparv/#advanced=false&hash=
        fccea59f54ed3a21859449b148368f9e4cb5f5af&input=xml&lang=sv&language=sv
        Change hash if updating settings variable."""
        settings: str = json.dumps(
            {
                "corpus": "untitled",
                "lang": "sv",
                "textmode": "xml",
                "word_segmenter": "default_tokenizer",
                "sentence_segmentation": {
                    "tag": "sentence",
                    "attributes": ["original"],
                },
                "paragraph_segmentation": {"tag": "paragraph", "attributes": ["name"]},
                "root": {"tag": "text", "attributes": ["title"]},
                "extra_tags": [],
                "positional_attributes": {
                    "lexical_attributes": ["pos", "msd", "lemma", "lex", "sense"],
                    "compound_attributes": ["complemgram", "compwf"],
                    "dependency_attributes": ["ref", "dephead", "deprel"],
                    "sentiment": ["sentiment", "sentimentclass"],
                },
                "named_entity_recognition": ["ex", "type", "subtype"],
                "text_attributes": {"readability_metrics": ["lix", "ovix", "nk"]},
            }
        )
        response: requests.models.Response = requests.get(
            "https://ws.spraakbanken.gu.se/ws/sparv/v2/",
            data={
                "text": self._sparv_convert_document_to_xml(),
                "mode": "xml",
                "settings": settings,
            },
        )
        if response.status_code == 200:
            sparv_data: str = response.text.strip()
            return ET.fromstring(sparv_data)

        raise Exception(f"Sparv returned unexpected code: {response.status_code}")

    def get_regex_position(self, regex) -> Tuple[int, int]:
        """Returns the start and end position of the first match of regex."""
        match: Optional[Match[str]] = re.search(regex, self.to_text())
        if match:
            return match.span()
        return 0, 0

    def get_regex_postions(self, regex) -> List[Tuple[int, int]]:
        """Returns the start and end postions of all found regex matches."""
        matches: Iterator[Match[str]] = re.finditer(regex, self.to_text())
        return [match.span() for match in matches]

    def get_headline_position(self, headline: Headline) -> Tuple[int, int]:
        """Returns the start and end postion of the headline, not its sub text."""
        return self.get_regex_position(headline.name)

    def get_word_postion(self, word: Word) -> Tuple[int, int]:
        """Get start and end position of the word in the report."""
        text: str = self.to_text()
        words: List[Word] = self.get_words()
        current_position: int = 0

        for w in words:
            current_position = text.find(w.text, current_position)

            if w == word:
                return (current_position, current_position + len(w.text))
        return 0, 0

    def get_words(self, skip_wordclasses: List[str] = []) -> List[Word]:
        return [
            word
            for headline in self.headlines
            for sentence in headline.sentences
            for word in sentence.words
            if word.wordclass not in skip_wordclasses
        ]

    def spellcheck(self, skip_wordclasses: List[str]) -> Dict[Word, List[str]]:
        """Run the stava spellchecker and return a list of incorrectly spelled word objects and
        suggestions for alternative spellings."""
        # open temp file to store text
        file: IO[Any] = tempfile.NamedTemporaryFile(delete=False)
        file.write(self.to_text().encode("utf-8"))
        tmp_path: str = file.name
        file.close()

        # run stava on temp file and parse the output
        args = [
            "stava",
            "-r",  # include corrections
            "-f",  # include abbreviations
            "-n",  # include common names
            tmp_path,
        ]
        output = subprocess.run(args, stdout=subprocess.PIPE)
        stava_results: Dict[Word, List[str]] = {}
        for line in output.stdout.decode("utf-8").split("\n"):
            match: Optional[Match] = re.match(r"^(.+): (.+)$", line)
            if match and "?" in match.group(2):
                stava_results[match.group(1)] = []
            elif match:
                stava_results[match.group(1)] = match.group(2).split(" ")

        # link word objects to errors and suggestions
        results: Dict[Word, List[str]] = {}
        for error, corrections in stava_results.items():
            for word in self.get_words(skip_wordclasses):
                if word.text == error:
                    results[word] = corrections
        return results

    def to_text(self) -> str:
        return "\n\n".join([headline.to_text() for headline in self.headlines]).strip()
