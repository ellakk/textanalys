class Analyzer:
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
        "TVÅNGSMEDEL": {"order": 0, "required": False, "dependencies": []},
        "VIDTAGNA ÅTGÄRDER": {"order": 0, "required": False, "dependencies": []},
        "ERSÄTTNINGSYRKAN": {"order": 6, "required": False, "dependencies": []},
        "BILAGOR": {"order": 0, "required": False, "dependencies": []},
        "ÖVRIGT": {"order": 7, "required": False, "dependencies": []},
        "HATBROTT": {"order": 0, "required": False, "dependencies": []},
        "TILLGRIPET GODS": {"order": 0, "required": False, "dependencies": []},
        "HÄNDELSEN": {"order": 3, "required": False, "dependencies": []},
        "PARTERNAS INBÖRDES FÖRHÅLLANDE": {
            "order": 0,
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
        self.document = document
        self.errors = []
        self.stop_on_error = stop_on_error

    def add_error(self, message, headline=None):
        self.errors.append({"message": message, "headline": headline})

    def has_errors(self):
        if self.errors:
            return True
        return False

    def run(self):
        tests = [self.test_headline_case, self.test_headline]

        for test in tests:
            if self.stop_on_error and self.has_errors():
                break
            test()

    def test_headline(self):
        for headline in self.document:
            if not headline in self.headlines:
                self.add_error(
                    "{} är inte en valid rubrik enligt polisens direktiv".format(
                        headline
                    )
                )

    def test_headline_case(self):
        for headline in self.document:
            if not headline.isupper():
                self.add_error(
                    "Rubriken {} är inte skriven i varsaler".format(headline)
                )
