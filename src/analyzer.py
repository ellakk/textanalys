import re
from typing import List, Optional, Union, Tuple, Dict, Any, Match, Pattern, Callable

from src.report.report import Report
from src.report.word import Word
from src.report.headline import Headline
from src.rules.rules import Rules
from src.rules.rule_structures import HeadlineRules


class Analyzer:
    """Class for analysing documents."""

    def __init__(self, report: Report, stop_on_error: bool = False) -> None:
        """Instantiate the object. The report argument is a dict where the keys are
        the header of the documents and the value is a list of paragraphs under the
        heading."""
        self.report: Report = report
        self.errors: List[Dict[str, Union[str, int]]] = []
        self.stop_on_error: bool = stop_on_error

    def add_error(
        self,
        message: str,
        position: Optional[Tuple[int, int]] = None,
        headline: Optional[Headline] = None,
        word: Optional[Word] = None,
    ) -> None:
        """Add an error to the error list."""
        start: int = 0
        end: int = 0

        if position:
            start, end = position
        elif headline:
            start, end = self.report.get_headline_position(headline)
        elif word:
            start, end = self.report.get_word_postion(word)
        self.errors.append({"message": message, "start": start, "end": end})

    def get_analysis(self) -> Dict[str, Any]:
        """The result of the analysis as a dict. Formatted to be used as an API reponse.
        """
        return {
            "report": self.report.to_text(),
            "errors": self.errors,
            "has_errors": self.has_errors(),
        }

    def has_errors(self) -> bool:
        """Returns a boolean representing if the analyzer has found errors or not."""
        if self.errors:
            return True
        return False

    def run(self) -> None:
        """Runs a full analysis on the document."""
        tests: List[Callable[[], None]] = [
            self.test_headlines_case,
            self.test_headlines_predefined,
            self.test_headlines_required,
            self.test_headlines_dependencies,
            self.test_headlines_order,
            self.test_reading_attributes,
            self.test_forbidden_words,
        ]

        for test in tests:
            if self.stop_on_error and self.has_errors():
                break
            test()

    def test_headlines_case(self) -> None:
        """Test to make sure the headlines are written in uppercase."""
        for headline in self.report.headlines:
            if not headline.name.isupper():
                self.add_error(
                    f"Rubriken {headline.name} är inte skriven i versaler",
                    headline=headline,
                )

    def test_headlines_predefined(self) -> None:
        """Test to make sure the headlines exists in the list of predefined ones."""
        for headline in self.report.headlines:
            if not Rules.get_headline_rules(headline.name):
                self.add_error(
                    f"{headline.name} är inte en valid rubrik.", headline=headline
                )

    def test_headlines_required(self) -> None:
        """Make sure required headlines are present."""
        for rule in Rules.headlines:
            if not rule.required:
                continue
            is_match: bool = False
            for headline in self.report.headlines:
                if Rules.get_headline_rules(headline.name) == rule:
                    is_match = True
                    break
            if not is_match:
                self.add_error(f"Rubriken {rule.name} som måste vara med saknas.")

    def test_headlines_dependencies(self) -> None:
        """Test if the headlines dependencies are satified."""

        def has_dep(dep: str) -> bool:
            for h in self.report.headlines:
                if Rules.get_headline_rules(h.name) == Rules.get_headline_rules(dep):
                    return True
            return False

        for headline in self.report.headlines:
            rule: Optional[HeadlineRules] = Rules.get_headline_rules(headline.name)
            if not rule:
                continue

            for dependency_group in rule.dependencies:
                is_match: bool = False
                for dependency in dependency_group:
                    if has_dep(dependency):
                        is_match = True
                        break
                if not is_match:
                    dependencies_list: str = ", ".join(dependency_group)
                    self.add_error(
                        f"Rubriken {headline.name} kräver att en av följande "
                        f"rubriker finns med i dokumentet: {dependencies_list}.",
                        headline=headline,
                    )

    def test_headlines_order(self) -> None:
        """Test if the headlines are in correct order."""
        last: Tuple[int, str] = (0, "")

        for headline in self.report.headlines:
            rule: Optional[HeadlineRules] = Rules.get_headline_rules(headline.name)
            if (not rule) or (rule.order is None):
                continue

            last_order, last_headline = last  # type: int, str
            if last_order > rule.order:
                self.add_error(
                    (
                        f"Rubriken {headline.name} ska komma före "
                        f"rubriken {last_headline}."
                    ),
                    headline=headline,
                )

            last = (rule.order, headline.name)

    def test_reading_attributes(self) -> None:
        """Test if the reading attributes of the text passes the min,max rules
        of LIX."""
        if self.report.lix > Rules.lix_max:
            self.add_error(
                "LIX värdet för rapporten är högt. Försök korta ner meningarna."
            )

        if self.report.lix < Rules.lix_min:
            self.add_error(
                "LIX värdet för rapporten är lågt. Försök skriva längre meningar."
            )

    def test_forbidden_words(self) -> None:
        """Test if a list of forbidden words exists in text."""
        # Move this to a separate file
        forbidden_words = ["neger"]

        pads = ["'", '"', "”"]
        pad_open = False
        for word in self.report.get_words():
            if word.text in pads:
                pad_open = not pad_open
                continue
            if pad_open:
                continue
            if word.text in forbidden_words:
                self.add_error(
                    f"Ordet {word.text} får endast förekomma i citat.", word=word
                )
