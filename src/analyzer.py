class Analyzer:
    """Class for analysing documents."""

    # All headlines
    headlines = {
        "INLEDNING": {"order": 1, "required": True, "dependencies": []},
        "BROTTET": {"order": 2, "required": False, "dependencies": []},
        "BROTTEN": {"order": 2, "required": False, "dependencies": []},
        "SIGNALEMENT": {"order": 5, "required": False, "dependencies": []},
        "SKADOR": {"order": 4, "required": False, "dependencies": []},
        "BROTTSPLATSUNDERSÖKNING": {
            "order": None,
            "required": False,
            "dependencies": [],
        },
        "TVÅNGSMEDEL": {"order": -1, "required": False, "dependencies": []},
        "VIDTAGNA ÅTGÄRDER": {"order": -1, "required": False, "dependencies": []},
        "ERSÄTTNINGSYRKAN": {"order": 6, "required": False, "dependencies": []},
        "BILAGOR": {"order": -1, "required": False, "dependencies": []},
        "ÖVRIGT": {"order": 7, "required": False, "dependencies": []},
        "HATBROTT": {"order": -1, "required": False, "dependencies": []},
        "TILLGRIPET GODS": {"order": -1, "required": False, "dependencies": []},
        "HÄNDELSEN": {"order": 3, "required": False, "dependencies": []},
        "PARTERNAS INBÖRDES FÖRHÅLLANDE": {
            "order": -1,
            "required": False,
            "dependencies": [],
        },
        "TIDIGARE HÄNDELSER": {"order": 1, "required": False, "dependencies": []},
        "ÅTALSANGIVELSE": {"order": 1, "required": False, "dependencies": []},
        "HÄNDELSEFÖRLOPP ENLIGT XX": {
            "order": 4,
            "required": False,
            "dependencies": [],
        },
        "VITTNESIAKTTAGELSER": {"order": 1, "required": False, "dependencies": []},
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
        tests = [self.test_headlines_case, self.test_headlines, self.test_headlines_required]

        for test in tests:
            if self.stop_on_error and self.has_errors():
                break
            test()

    def test_headlines(self):
        """Test to make sure the headlines exists in the list of headlines predefined by
        the police."""
        for headline in self.document:
            if not headline.upper() in self.headlines:
                self.add_error(
                    f"{headline} är inte en valid rubrik enligt polisens direktiv.", headline)

    def test_headlines_case(self):
        """Test to make sure the headlines are written in uppercase."""
        for headline in self.document:
            if not headline.isupper():
                self.add_error(f"Rubriken {headline} är inte skriven i varsaler", headline)

    def test_headlines_required(self):
        """Make sure required headlines are present."""
        for headline, config in self.headlines.items():
            if config['required'] and headline not in self.document:
                self.add_error(f"Rubriken {headline} som måste vara med saknas.")
