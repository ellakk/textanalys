import re


class Analyzer:
    """Class for analysing documents."""

    reading_attributes_rules = {
        "lix": {"min": 32.6, "max": 56.7},
        "ovix": {"min": 47.8, "max": 82.7},
        "nk": {"min": 0.65, "max": 3.73},
    }

    # All headline
    headline_rules = {
        "INLEDNING": {
            "regex": re.compile(r"inledning", re.I),
            "order": 1,
            "required": True,
            "dependencies": [],
        },
        "BROTTET": {
            "regex": re.compile(r"brottet", re.I),
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
            "dependencies": [["BROTTET", "BROTTEN", "HÄNDELSEN"]],
        },
        "SKADOR": {
            "regex": re.compile(r"skador", re.I),
            "order": 4,
            "required": False,
            "dependencies": [],
        },
        "BROTTSPLATSUNDERSÖKNING": {
            "regex": re.compile(r"brottsplatsundersökning", re.I),
            "order": -1,
            "required": False,
            "dependencies": [["BROTTET", "BROTTEN"]],
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
            "regex": re.compile(r"bilagor|bilaga", re.I),
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
            "order": 2,
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
            "order": 3,
            "required": False,
            "dependencies": [],
        },
    }

    def __init__(self, report, stop_on_error=False):
        """Instantiate the object. The report argument is a dict where the keys are
        the header of the documents and the value is a list of paragraphs under the
        heading."""
        self.report = report
        self.errors = []
        self.stop_on_error = stop_on_error

    def add_error(self, message, regex=""):
        """Add an error to the error list."""
        start, end = 0, 0

        if regex:
            start, end = self.report.get_regex_position(regex)
        self.errors.append({"message": message, "start": start, "end": end})

    def get_headline_rules(self, headline):
        """Return the rules for headline if found."""
        for rules in self.headline_rules.values():
            if rules["regex"].match(headline):
                return rules
        return {}

    def get_analysis(self):
        """The result of the analysis as a dict. Formatted to be used as an API reponse."""
        return {
            "report": self.report.to_text(),
            "errors": self.errors,
            "has_errors": self.has_errors(),
        }

    def has_errors(self):
        """Returns a boolean representing if the analyzer has found errors or not."""
        if self.errors:
            return True
        return False

    def headline_has_dependencies(self, dependencies):
        """Validates a list of dependencies, returns true if atleast one exist in the
        document.
        """
        for dependency in dependencies:
            for headline in self.report.headlines():
                if self.headline_rules[dependency]["regex"].match(headline):
                    return True
        return False

    def run(self):
        """Runs a full analysis on the document."""
        tests = [
            self.test_headlines_case,
            self.test_headlines,
            self.test_headlines_required,
            self.test_headlines_dependencies,
            self.test_headlines_order,
            self.test_reading_attributes,
        ]

        for test in tests:
            if self.stop_on_error and self.has_errors():
                break
            test()

    def test_headlines(self):
        """Test to make sure the headlines exists in the list of headlines predefined by
        the police."""
        for headline in self.report.headlines():
            is_match = False
            for rules in self.headline_rules.values():
                if rules["regex"].match(headline):
                    is_match = True
                    break
            if not is_match:
                self.add_error(
                    f"{headline} är inte en valid rubrik enligt polisens direktiv.",
                    regex=headline,
                )

    def test_headlines_case(self):
        """Test to make sure the headlines are written in uppercase."""
        for headline in self.report.headlines():
            if not headline.isupper():
                self.add_error(
                    f"Rubriken {headline} är inte skriven i versaler", regex=headline
                )

    def test_headlines_required(self):
        """Make sure required headlines are present."""
        for rule, rules in self.headline_rules.items():
            if not rules["required"]:
                continue
            is_match = False
            for headline in self.report.headlines():
                if rules["regex"].match(headline):
                    is_match = True
                    break
            if not is_match:
                self.add_error(f"Rubriken {rule} som måste vara med saknas.")

    def test_headlines_dependencies(self):
        """Test if the headlines dependencies are satified."""
        for headline in self.report.headlines():
            rules = self.get_headline_rules(headline)
            if not rules:
                continue

            for dependency in rules["dependencies"]:
                if not self.headline_has_dependencies(dependency):
                    dlist = ", ".join(dependency)
                    self.add_error(
                        f"Rubriken {headline} kräver att en av följande "
                        f"rubriker finns med i dokumentet: {dlist}.",
                        regex=headline,
                    )

    def test_headlines_order(self):
        """Test if the headlines are in correct order."""
        last = (0, "")

        for headline in self.report.headlines():
            rules = self.get_headline_rules(headline)
            if (not rules) or (rules["order"] == -1):
                continue

            last_order, last_headline = last
            if last_order > rules["order"]:
                self.add_error(
                    f"Rubriken {headline} ska komma före rubriken {last_headline}.",
                    regex=headline,
                )

            last = (rules["order"], headline)

    def test_reading_attributes(self):
        """Test if the reading attributes of the text passes the min,max rules of LIX,
        OVIX and NK."""
        reading_attributes = self.report.reading_attributes()

        if reading_attributes["lix"] > self.reading_attributes_rules["lix"]["max"]:
            self.add_error(
                "LIX värdet för rapporten är högt. Försök korta ner meningarna."
            )

        if reading_attributes["lix"] < self.reading_attributes_rules["lix"]["min"]:
            self.add_error(
                "LIX värdet för rapporten är lågt. Försök skriva längre meningar."
            )

        if reading_attributes["ovix"] > self.reading_attributes_rules["ovix"]["max"]:
            self.add_error(
                "OVIX värdet för rapporten är högt. Försök variera orden mindre."
            )

        if reading_attributes["ovix"] < self.reading_attributes_rules["ovix"]["min"]:
            self.add_error(
                "OVIX värdet för rapporten är lågt. Försk variera orden mera."
            )

        if reading_attributes["nk"] > self.reading_attributes_rules["nk"]["max"]:
            self.add_error(
                "Nominalkvoten för rapporten är högt. "
                "Försök använda mindre substantiv och fler verb."
            )

        if reading_attributes["nk"] < self.reading_attributes_rules["nk"]["min"]:
            self.add_error(
                "Nominalkvoten för rapporten är låg. "
                "Försök använda fler substantiv och mindre verb."
            )
