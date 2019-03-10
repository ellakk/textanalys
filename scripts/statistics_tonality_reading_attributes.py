"""Gather reading attributes and tonality from all documents located in PATH
directory. Dumps to stats* json files in directory from where this scripted is
invoked. Needs to be placed in root of the textanalys-back-end repository.

"""

import glob
import os
import json

from docx import Document
from src.report import Report

PATH = "/home/kalle/Downloads/Arkiv/*"


def read_documents():
    documents = {}
    files = glob.glob(PATH)
    for filepath in files:
        documents[os.path.basename(filepath)] = Document(filepath)
    return documents


def gather_statistics(documents):
    statistics = {}
    failed = {}
    count = 1
    fail_count = 0
    total = len(documents.keys())

    for filename, document in documents.items():
        print(f"Now analyzing document: {count}/{total}, failed: {fail_count}")
        count += 1
        try:
            report = Report(document)
            statistics[filename] = {
                "tonality": report.tonality(),
                "reading_attributes": report.reading_attributes(),
            }
        except Exception as error:
            fail_count += 1
            failed[filename] = {'text': report.to_text(),
                                'error': str(error)}
    return (statistics, failed)


def run():
    documents = read_documents()
    statistics, failed = gather_statistics(documents)
    with open("stats.json", "w") as file:
        json.dump(statistics, file, ensure_ascii=False)
    with open("stats_errors.json", "w") as file:
        json.dump(failed, file, ensure_ascii=False)

run()
