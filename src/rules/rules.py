from typing import List, Optional

from src.rules.rule_structures import HeadlineRules, NamedEntityRule


class Rules:
    """All the rules for the report. The class is static since nothing is supposed to change
    and should never be instansiated."""

    headlines: List[HeadlineRules] = []
    lix_max: float
    lix_min: float
    spelling_skip_wordclasses: List[str] = []

    def __init__(self):
        self._init_headline_rules()
        self._init_lix()
        self._init_spell_skip()

    def _init_headline_rules(self):
        self.headlines.append(
            HeadlineRules(
                "INLEDNING",
                order=1,
                required=True,
                named_entities=[
                    NamedEntityRule(
                        "Texten under rubriken INLEDNING behöver en tidpunkt.",
                        identity="TIMEX",
                        cheat=r"\d{1,2}[:|\.]\d{1,2}",
                    ),
                    NamedEntityRule(
                        "Texten under rubriken INLEDNING behöver en adress.",
                        identity="ENAMEX",
                        type="LOC",
                    ),
                ],
            )
        )
        self.headlines.append(HeadlineRules("ÅTALSANGIVELSE", order=2))
        self.headlines.append(HeadlineRules("BROTTET", order=2))
        self.headlines.append(HeadlineRules("BROTTEN", order=2))
        self.headlines.append(HeadlineRules("HÄNDELSEN", order=2))
        self.headlines.append(HeadlineRules("TIDIGARE HÄNDELSER", order=3))
        self.headlines.append(HeadlineRules("VITTNESIAKTTAGELSER", order=3))
        self.headlines.append(
            HeadlineRules(
                "HÄNDELSEFÖRLOPP ENLIGT XX", regex="händelseförlopp enlight.+", order=3
            )
        )
        self.headlines.append(HeadlineRules("SKADOR", order=4))
        self.headlines.append(
            HeadlineRules(
                "SIGNALEMENT",
                order=5,
                dependencies=[["BROTTET", "BROTTEN", "HÄNDELSEN"]],
            )
        )
        self.headlines.append(
            HeadlineRules(
                "ERSÄTTNINGSYRKAN", regex="ersättningsyrkan|ersättningsyrkande", order=6
            )
        )
        self.headlines.append(HeadlineRules("ÖVRIGT", order=7))
        self.headlines.append(
            HeadlineRules("BILAGOR", regex="bilagor|bilaga", order=9999)
        )

        self.headlines.append(
            HeadlineRules(
                "BROTTSPLATSUNDERSÖKNING", dependencies=[["BROTTET", "BROTTEN"]]
            )
        )
        self.headlines.append(HeadlineRules("TVÅNGSMEDEL"))
        self.headlines.append(HeadlineRules("VIDTAGNA ÅTGÄRDER"))
        self.headlines.append(HeadlineRules("HATBROTT"))
        self.headlines.append(HeadlineRules("TILLGRIPET GODS"))
        self.headlines.append(HeadlineRules("PARTERNAS INBÖRDES FÖRHÅLLANDE"))

    def _init_lix(self):
        self.lix_max = 56.7
        self.lix_min = 32.6

    def _init_spell_skip(self):
        self.spelling_skip_wordclasses.append("PM")  # names
        self.spelling_skip_wordclasses.append("AN")  # abbreviations

    def get_headline_rules(self, candidate: str) -> Optional[HeadlineRules]:
        """Try to get the headline rules matching the candidate."""
        for headline in self.headlines:
            if headline.matches(candidate):
                return headline
        return None
