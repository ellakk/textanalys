import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from fuzzywuzzy import fuzz, process

from src.report.headline import Headline
from src.report.report import Report
from src.report.word import Word
from src.rules.rule_structures import HeadlineRules
from src.rules.rules import Rules


class Analyzer:
    """Class for analysing documents."""

    def __init__(self, report: Report, stop_on_error: bool = False) -> None:
        """Instantiate the object. The report argument is a dict where the keys are
        the header of the documents and the value is a list of paragraphs under the
        heading."""
        self.rules = Rules()
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
        self.test_sanity()
        if self.has_errors():
            return

        tests: List[Callable[[], None]] = [
            self.test_headlines_predefined,
            self.test_headlines_required,
            self.test_headlines_dependencies,
            self.test_headlines_order,
            self.test_headlines_named_entities,
            self.test_reading_attributes,
            self.test_forbidden_words,
            self.test_unwanted_words,
            self.test_spelling,
            self.test_grammar_rules_regex,
        ]

        for test in tests:
            if self.stop_on_error and self.has_errors():
                break
            test()

    def test_sanity(self) -> None:
        """Test to se if the document has the proper format and can be used in the other
        tests."""
        if self.report.headlines:
            return

        if self.report.document.paragraphs:
            self.add_error(
                "Rubrikerna i dokumentet är felformaterade eller saknas. "
                "Rubrikerna ska vara skrivna i versaler och ha samma "
                "typsnitt, stil och storlek som brödtexten."
            )

        if not self.report.document.paragraphs:
            self.add_error("Ditt dokument är antigen tomt eller i fel format.")

    def test_headlines_predefined(self) -> None:
        """Test to make sure the headlines exists in the list of predefined ones."""
        for headline in self.report.headlines:
            if not self.rules.get_headline_rules(headline.name):
                headlines = [headline.name for headline in self.rules.headlines]
                suggestion, _ = process.extractOne(
                    headline.name, headlines, scorer=fuzz.partial_ratio
                )
                self.add_error(
                    f"{headline.name} är inte en valid rubrik. "
                    f"Rättningsförlsag: {suggestion}.",
                    headline=headline,
                )
            elif re.search("\\W{1,}", headline.name, re.I):
                self.add_error(
                    f"Rubriken {headline.name} innehåller tecken som inte är "
                    "alfanumeriska vilket inte är tillåtet för en rubrik.",
                    headline=headline,
                )

    def test_headlines_required(self) -> None:
        """Make sure required headlines are present."""
        for rule in self.rules.headlines:
            if not rule.required:
                continue
            is_match: bool = False
            for headline in self.report.headlines:
                if self.rules.get_headline_rules(headline.name) == rule:
                    is_match = True
                    break
            if not is_match:
                self.add_error(f"Rubriken {rule.name} som måste vara med saknas.")

    def test_headlines_dependencies(self) -> None:
        """Test if the headlines dependencies are satified."""

        def has_dep(dep: str) -> bool:
            for h in self.report.headlines:
                if self.rules.get_headline_rules(
                    h.name
                ) == self.rules.get_headline_rules(dep):
                    return True
            return False

        for headline in self.report.headlines:
            rule: Optional[HeadlineRules] = self.rules.get_headline_rules(headline.name)
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
            rule: Optional[HeadlineRules] = self.rules.get_headline_rules(headline.name)
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

    def test_headlines_named_entities(self) -> None:
        """Test if the headlines required named entities are present."""
        for headline in self.report.headlines:
            rule: Optional[HeadlineRules] = self.rules.get_headline_rules(headline.name)
            if not (rule and rule.named_entities):
                continue

            for ne_rule in rule.named_entities:
                if headline.has_named_entity(
                    ne_rule.identity, ne_rule.type, ne_rule.subtype
                ):
                    continue
                if ne_rule.cheat and re.search(ne_rule.cheat, headline.to_text()):
                    continue
                self.add_error(ne_rule.message, headline=headline)

    def test_reading_attributes(self) -> None:
        """Test if the reading attributes of the text passes the min,max rules
        of LIX."""
        if self.report.lix > self.rules.lix_max:
            self.add_error(
                "LIX värdet för rapporten är högt. Försök korta ner meningarna."
            )

        if self.report.lix < self.rules.lix_min:
            self.add_error(
                "LIX värdet för rapporten är lågt. Försök skriva längre meningar."
            )

    def test_forbidden_words(self) -> None:
        """Test if there are any sensitive/swear words outside of the citations."""
        pad_open: bool = False
        for word in self.report.get_words():
            if word.text in self.rules.citation_delimiters:
                pad_open = not pad_open
                continue
            if pad_open:
                continue
            if (word.text in self.rules.forbidden_words) or any(
                [b in self.rules.forbidden_words for b in word.baseform]
            ):
                self.add_error(
                    f"Ordet {word.text} får endast förekomma i citat.", word=word
                )

    def test_unwanted_words(self) -> None:
        """Test if there are any unwanted words outside of the citations and report them with a
        suggestion what to use instead."""
        pad_open: bool = False
        for word in self.report.get_words():
            if word.text in self.rules.citation_delimiters:
                pad_open = not pad_open
                continue
            if pad_open:
                continue
            for u_word in self.rules.unwanted_words:
                if word.text == u_word["word"]:
                    self.add_error(
                        f"Ordet {word.text} är inte tillåtet, "
                        f"använd hellre: {u_word['alternative']}.",
                        word=word,
                    )
                    break

    def test_spelling(self) -> None:
        """Test the spelling in the report."""
        misstakes: Dict[Word, List[str]] = self.report.spellcheck(
            self.rules.spelling_skip_wordclasses
        )
        for word, corrections in misstakes.items():
            if word.text in self.rules.forbidden_words:
                continue
            error_text: str = f"Ordet {word.text} är felstavat."
            if corrections:
                error_text += " Rättningsförslag: " + ", ".join(corrections)
            self.add_error(error_text, word=word)

    def test_grammar_rules_regex(self) -> None:
        """Test grammatical rules by matching against regex'es."""
        for rule in self.rules.grammar_regex:
            positions: List[Tuple[int, int]] = self.report.get_regex_postions(
                rule["regex"]
            )
            for position in positions:
                self.add_error(rule["message"], position=position)
