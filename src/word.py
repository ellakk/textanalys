class Word:
    def __init__(self, word, wordclass, morphosyntax, baseform, attitude, dependency_relation, reference, dependency_head):
        self.word = word
        self.wordclass = wordclass
        self.morphosyntax = morphosyntax
        self.baseform = baseform
        self.attitude = attitude
        self.dependency_relation = dependency_relation
        self.reference = reference
        self.dependency_head = dependency_head

    @classmethod
    def from_xml(cls, xml):
        """Check https://spraakbanken.gu.se/swe/forskning/infrastruktur/sparv/annotationer
        for more attributes and what the current ones mean."""
        parse_attributes = lambda aa : [a for a in aa.split('|') if a]

        word = xml.text
        wordclass = xml.attrib['pos']
        morphosyntax = xml.attrib['msd']
        baseform = parse_attributes(xml.attrib['lemma'])
        attitude = xml.attrib['sentimentclass']
        dependency_relation = xml.attrib['deprel']
        reference = xml.attrib['ref']
        dependency_head = xml.attrib['dephead']

        return cls(word, wordclass, morphosyntax, baseform, attitude, dependency_relation, reference, dependency_head)
