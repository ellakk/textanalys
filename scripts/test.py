"""Play around with different classes in the code base. Not a real test, rather used to
debugg varioues issuess as they arise. This file needs to be moved to the root of the
repository to run.
"""

from docx import Document

from src.report.report import Report


def main():
    document = Document("./test/docs/test_ok_report.docx")
    report = Report(document)
    words = report.get_words()


if __name__ == "__main__":
    main()
