from typing import List, Optional

from src.rules.rule_structures import HeadlineRules, NamedEntityRule


class Rules:
    """All the rules for the report. The class is static since nothing is supposed to change
    and should never be instansiated."""
    headlines: List[HeadlineRules] = [
        HeadlineRules("INLEDNING",
                      order=1,
                      required=True,
                      named_entities=[NamedEntityRule("Texten under rubriken INLEDNING behöver en tidpunkt", "TIMEX", cheat=r"\d{1,2}[:|\.]\d{1,2}")]),
        HeadlineRules("ÅTALSANGIVELSE", order=2),
        HeadlineRules("BROTTET", order=2),
        HeadlineRules("BROTTEN", order=2),
        HeadlineRules("HÄNDELSEN", order=2),
        HeadlineRules("TIDIGARE HÄNDELSER", order=3),
        HeadlineRules("VITTNESIAKTTAGELSER", order=3),
        HeadlineRules("HÄNDELSEFÖRLOPP ENLIGT XX", regex="händelseförlopp enlight.+", order=3),
        HeadlineRules("SKADOR", order=4),
        HeadlineRules("SIGNALEMENT", order=5, dependencies=[["BROTTET", "BROTTEN", "HÄNDELSEN"]]),
        HeadlineRules("ERSÄTTNINGSYRKAN", regex="ersättningsyrkan|ersättningsyrkande", order=6),
        HeadlineRules("ÖVRIGT", order=7),
        HeadlineRules("BILAGOR", regex="bilagor|bilaga", order=9999),

        HeadlineRules("BROTTSPLATSUNDERSÖKNING", dependencies=[["BROTTET", "BROTTEN"]]),
        HeadlineRules("TVÅNGSMEDEL"),
        HeadlineRules("VIDTAGNA ÅTGÄRDER"),
        HeadlineRules("HATBROTT"),
        HeadlineRules("TILLGRIPET GODS"),
        HeadlineRules("PARTERNAS INBÖRDES FÖRHÅLLANDE"),
    ]
    lix_max: float = 56.7
    lix_min: float = 32.6
    spelling_skip_wordclasses: List[str] = [
        "PM",  # names
        "AN"   # abbreviation
    ]

    @classmethod
    def get_headline_rules(cls, candidate: str) -> Optional[HeadlineRules]:
        """Try to get the headline rules matching the candidate."""
        for headline in cls.headlines:
            if headline.matches(candidate):
                return headline
        return None
