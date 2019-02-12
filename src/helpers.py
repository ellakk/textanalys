import re
from collections import OrderedDict
from io import BytesIO

from docx import Document


def parse_docx(docx):
    """Parse a docx file. Argument to parameter docx has to be a file handle.
    Returns an ordered dictionary where the keys are the headlines and the
    values are lists containing all the paragraph under each headline.

    """
    source_stream = BytesIO(docx.read())
    document = Document(source_stream)
    source_stream.close()

    parsed_document = OrderedDict()
    for paragraph in document.paragraphs:
        current_headline = parsed_document and list(parsed_document.keys())[-1]
        text = paragraph.text.strip()

        if re.match(r"(^\w+\s?\w+\s?\w+\s?$)", text):
            parsed_document[text] = []
        elif current_headline and text:
            parsed_document[current_headline].append(text)

    return parsed_document
