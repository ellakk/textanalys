import re
from collections import OrderedDict
from io import BytesIO
import xml.etree.ElementTree as ET

import requests
from docx import Document


class Report:
    """Handles police reports. """

    def __init__(self, report):
        """Initialize the report. Argument to parameter report has to be a file handle
        of a .docx file.
        """
        source_stream = BytesIO(report.read())
        self.document = Document(source_stream)
        source_stream.close()

        self.data = self._init_data()
        self.sparv_xml = self._init_sparv_xml()

    def _init_data(self):
        """Intialize the data variable."""
        data = OrderedDict()
        for paragraph in self.document.paragraphs:
            current_headline = data and list(data.keys())[-1]
            text = paragraph.text.strip()

            if re.match(r"(^\w+\s?\w+\s?\w+\s?$)", text):
                data[text] = []
            elif current_headline and text:
                data[current_headline].append(text)

        return data

    def _init_sparv_xml(self):
        """Fetches information about the report from the Sparv API and returns it as an
        XML object."""
        response = requests.get(
            "https://ws.spraakbanken.gu.se/ws/sparv/v2/", data={"text": self.to_text()}
        )
        if response.status_code == 200:
            sparv_data = response.text.strip()
            return ET.fromstring(sparv_data)
        raise Exception(f"Sparv returned unexpected code: {response.status_code}")

    def count_sentences(self):
        """Returns a count of the amount of sentences found in the report."""
        text = self.to_text(headlines=False)
        count = text.count(".")
        # If the last sentence is missing a '.' (bilagor) then we want to count it too
        if text.rstrip()[-1] != ".":
            count += 1
        return count

    def get_regex_position(self, regex):
        """Returns the start and end position of regex."""
        report = self.to_text()

        match = re.search(regex, report)
        if match:
            return match.span()
        return (0, 0)

    def headlines(self):
        """Returns a list of headlines found in the report."""
        return self.data.keys()

    def reading_attributes(self):
        """Returns a dict with: nix, ovix, np with their respective values."""
        text_node = self.sparv_xml.find("corpus/text")
        return {k: float(v) for (k, v) in text_node.attrib.items()}

    def to_text(self, headlines=True):
        """Returns a text representation of the report."""
        text = ""

        for headline, paragraphs in self.data.items():
            if headlines:
                text += f"{headline}\n"
            text += "\n".join(paragraphs) + "\n\n"
        return text

    def tonality(self):
        """Returns a dict with containing the tonality count for the entire
        document."""
        text_node = self.sparv_xml.find("corpus/text")
        tonality = {"words": 0, "negative": 0, "neutral": 0, "positive": 0}

        for w in text_node.iter("w"):
            tonality["words"] += 1
            if w.attrib["sentimentclass"]:
                tonality[w.attrib["sentimentclass"]] += 1
        return tonality

    def words(self, base=True):
        """Returns a list of words found in text. If base it true it will also return
        the words base form."""
        words = []
        text_node = self.sparv_xml.find("corpus/text")
        for w in text_node.iter("w"):
            if len(w.text) <= 1:
                continue

            if not w.text in words:
                words.append(w.text)
            if base:
                for word in w.attrib["lemma"].split("|"):
                    if len(word) <= 1:
                        continue
                    if not word in words:
                        words.append(word)
        return words
