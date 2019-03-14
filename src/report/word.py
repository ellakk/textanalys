import xml.etree.ElementTree as ET


class Word:
    """Represents a word and its attributes based on information from Sparv.

    Check:
    https://spraakbanken.gu.se/swe/forskning/infrastruktur/sparv/annotationer
    For more informatin about what the attributes mean and additional ones that
    can be implemented.

    """

    def __init__(self, word_node: ET.Element) -> None:
        self.text = word_node.text
        self.wordclass = word_node.attrib['pos']
        self.morphosyntax = word_node.attrib['msd']
        self.baseform = [w for w in word_node.attrib['lemma'].split('|') if w]
        self.attitude = word_node.attrib['sentimentclass']
        self.dependency_relation = word_node.attrib['deprel']
        self.reference = word_node.attrib['ref']
        self.dependency_head = word_node.attrib['dephead']
