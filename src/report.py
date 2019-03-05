import re
from collections import OrderedDict
from io import BytesIO

from docx import Document


class Report:
    data = OrderedDict()
    document = None

    def __init__(self, report):
        """Initialize the report. Argument to parameter report has to be a file handle
        of a .docx file.
        """
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
        return self.data.keys()

    def count_sentences(self):
        text = self.to_text(headlines=False)
        count = text.count(".")
        # If the last sentence is missing a '.' (bilagor) then we want to count it too
        if text.rstrip()[-1] != ".":
            count += 1
        return count

    def to_text(self, headlines=True):
        text = ""

        for headline, paragraphs in self.data.items():
            if headlines:
                text += f"{headline}\n"
            text += "\n".join(paragraphs) + "\n"

        return text
