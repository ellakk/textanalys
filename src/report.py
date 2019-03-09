import re
from collections import OrderedDict
from io import BytesIO

from docx import Document


class Report:
    """Handles police reports. """

    def __init__(self, report):
        """Initialize the report. Argument to parameter report has to be a file handle
        of a .docx file.
        """
        self.data = OrderedDict()
        source_stream = BytesIO(report.read())
        self.document = Document(source_stream)
        source_stream.close()

        for paragraph in self.document.paragraphs:
            current_headline = self.data and list(self.data.keys())[-1]
            text = paragraph.text.strip()

            if re.match(r"(^\w+\s?\w+\s?\w+\s?$)", text):
                self.data[text] = []
            elif current_headline and text:
                self.data[current_headline].append(text)

    def headlines(self):
        """Returns a list of headlines found in the report."""
        return self.data.keys()

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

    def to_text(self, headlines=True):
        """Returns a text representation of the report."""
        text = ""

        for headline, paragraphs in self.data.items():
            if headlines:
                text += f"{headline}\n"
            text += "\n".join(paragraphs) + "\n\n"

        return text
