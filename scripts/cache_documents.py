""" Cache all docx files in Sparv found in DOC_PATH. Should be placed in root of repo to run.
"""

import os

from docx import Document

from src.report.report import Report

DOC_PATH = "docx"


def get_document_list():
    documents = []
    for f_name in os.listdir(DOC_PATH):
        if f_name.endswith(".docx"):
            documents.append(f_name)
    return documents


def create_reports(files):
    count = len(files)
    for file in files:
        print(f"{count} reports left...")
        count -= 1
        document = Document(f"{DOC_PATH}/{file}")
        Report(document)


def main():
    files = get_document_list()
    create_reports(files)


if __name__ == "__main__":
    main()
