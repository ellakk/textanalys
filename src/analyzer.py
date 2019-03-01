import re


class Analyzer:
    """Class for analysing documents."""

    # All headlines
    headlines = {
        "INLEDNING": {
            "regex": re.compile(r"inledning", re.I),
            "order": 1,
            "required": True,
            "dependencies": [],
        },
        "BROTTET": {
            "regex": re.compile(r"brott|brottet", re.I),
            "order": 2,
            "required": False,
            "dependencies": [],
        },
        "BROTTEN": {
            "regex": re.compile(r"brotten", re.I),
            "order": 2,
            "required": False,
            "dependencies": [],
        },
        "SIGNALEMENT": {
            "regex": re.compile(r"signalement", re.I),
            "order": 5,
            "required": False,
            "dependencies": [],
        },
        "SKADOR": {
            "regex": re.compile(r"skador", re.I),
            "order": 4,
            "required": False,
            "dependencies": [],
        },
        "BROTTSPLATSUNDERSÖKNING": {
            "regex": re.compile(r"brottsplatsundersökning", re.I),
            "order": None,
            "required": False,
            "dependencies": [],
        },
        "TVÅNGSMEDEL": {
            "regex": re.compile(r"tvångsmedel", re.I),
            "order": -1,
            "required": False,
            "dependencies": [],
        },
        "VIDTAGNA ÅTGÄRDER": {
            "regex": re.compile(r"vidtagna åtgärder", re.I),
            "order": -1,
            "required": False,
            "dependencies": [],
        },
        "ERSÄTTNINGSYRKAN": {
            "regex": re.compile(r"ersättningsyrkan|ersättningsyrkande", re.I),
            "order": 6,
            "required": False,
            "dependencies": [],
        },
        "BILAGOR": {
            "regex": re.compile(r"bilagor", re.I),
            "order": -1,
            "required": False,
            "dependencies": [],
        },
        "ÖVRIGT": {
            "regex": re.compile(r"övrigt", re.I),
            "order": 7,
            "required": False,
            "dependencies": [],
        },
        "HATBROTT": {
            "regex": re.compile(r"hatbrott", re.I),
            "order": -1,
            "required": False,
            "dependencies": [],
        },
        "TILLGRIPET GODS": {
            "regex": re.compile(r"tillgripet gods", re.I),
            "order": -1,
            "required": False,
            "dependencies": [],
        },
        "HÄNDELSEN": {
            "regex": re.compile(r"händelsen", re.I),
            "order": 3,
            "required": False,
            "dependencies": [],
        },
        "PARTERNAS INBÖRDES FÖRHÅLLANDE": {
            "regex": re.compile(r"parternas inbördes förhållande", re.I),
            "order": -1,
            "required": False,
            "dependencies": [],
        },
        "TIDIGARE HÄNDELSER": {
            "regex": re.compile(r"tidigare händelser", re.I),
            "order": 1,
            "required": False,
            "dependencies": [],
        },
        "ÅTALSANGIVELSE": {
            "regex": re.compile(r"åtalsangivelse", re.I),
            "order": 1,
            "required": False,
            "dependencies": [],
        },
        "HÄNDELSEFÖRLOPP ENLIGT XX": {
            "regex": re.compile(r"händelseförlopp enlight.+", re.I),
            "order": 4,
            "required": False,
            "dependencies": [],
        },
        "VITTNESIAKTTAGELSER": {
            "regex": re.compile(r"vittnesiakttagelser", re.I),
            "order": 1,
            "required": False,
            "dependencies": [],
        },
    }

    def __init__(self, document, stop_on_error=False):
        """Instantiate the object. The document argument is a dict where the keys are
        the header of the documents and the value is a list of paragraphs under the
        heading."""
        self.document = document
        self.errors = []
        self.stop_on_error = stop_on_error

    def add_error(self, message, headline=None):
        """Add an error to the error list."""
        self.errors.append({"message": message, "headline": headline})

    def has_errors(self):
        """Returns a boolean representing if the analyzer has found errors or not."""
        if self.errors:
            return True
        return False

    def run(self):
        """Runs a full analysis on the document."""
        tests = [
            self.test_headlines_case,
            self.test_headlines,
            self.test_headlines_required,
        ]

        for test in tests:
            if self.stop_on_error and self.has_errors():
                break
            test()

    def test_headlines(self):
        """Test to make sure the headlines exists in the list of headlines predefined by
        the police."""
        for headline in self.document:
            is_match = False
            for rules in self.headlines.values():
                if rules['regex'].match(headline):
                    is_match = True
                    break
            if not is_match:
                self.add_error(
                    f"{headline} är inte en valid rubrik enligt polisens direktiv.",
                    headline,
                )


    def test_headlines_case(self):
        """Test to make sure the headlines are written in uppercase."""
        for headline in self.document:
            if not headline.isupper():
                self.add_error(
                    f"Rubriken {headline} är inte skriven i varsaler", headline
                )

    def test_headlines_required(self):
        """Make sure required headlines are present."""
        for headline, config in self.headlines.items():
            if config["required"] and headline not in self.document:
                self.add_error(f"Rubriken {headline} som måste vara med saknas.")
