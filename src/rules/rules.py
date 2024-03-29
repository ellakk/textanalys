from typing import List, Optional, Dict

import yaml

from src.rules.rule_structures import HeadlineRules, NamedEntityRule


class Rules:
    """All the rules for the report. The class is static since nothing is supposed to change
    and should never be instansiated."""

    def __init__(self):
        self.headlines: List[HeadlineRules] = []
        self._init_headline_rules()

        self.lix_max: float
        self.lix_min: float
        self.tonality_max: float
        self.tonality_min: float
        self.spelling_skip_wordclasses: List[str] = []
        self.citation_delimiters: List[str] = []
        self.grammar_rules: List[Dict[str, str]]
        self.named_entities: List[Dict[str, str]]
        with open("settings/rules/rules.yaml", "r") as file:
            rules = yaml.load(file, Loader=yaml.FullLoader)
            self.lix_min = rules["lix"]["min"]
            self.lix_max = rules["lix"]["max"]
            self.tonality_min = rules["tonality"]["min"]
            self.tonality_max = rules["tonality"]["max"]
            self.spelling_skip_wordclasses = rules["spelling_skip_wordclasses"]
            self.citation_delimiters = rules["citation_delimiters"]
            self.grammar_regex = rules["grammar_regex"]
            self.named_entities = rules["named_entities"]

        self.forbidden_words: List[str] = []
        with open("settings/rules/forbidden_words.yaml", "r") as file:
            self.forbidden_words = yaml.load(file, Loader=yaml.FullLoader)

        self.unwanted_words: List[Dict[str, str]]
        with open("settings/rules/unwanted_words.yaml", "r") as file:
            self.unwanted_words = yaml.load(file, Loader=yaml.FullLoader)

        self.police_abbreviations: List[Dict[str, str]]
        with open("settings/rules/police_abbreviations.yaml", "r") as file:
            self.police_abbreviations = yaml.load(file, Loader=yaml.FullLoader)

    def _init_headline_rules(self):
        rules = {}
        with open("settings/rules/headlines.yaml", "r") as file:
            rules = yaml.load(file, Loader=yaml.FullLoader)

        for hname, hrules in rules.items():
            if "named_entities" in hrules:
                hrules["named_entities"] = [
                    NamedEntityRule(**ne) for ne in hrules["named_entities"]
                ]

            self.headlines.append(
                HeadlineRules(name=hname, **hrules)
            )

    def get_headline_rules(self, candidate: str) -> Optional[HeadlineRules]:
        """Try to get the headline rules matching the candidate."""
        for headline in self.headlines:
            if headline.matches(candidate):
                return headline
        return None
