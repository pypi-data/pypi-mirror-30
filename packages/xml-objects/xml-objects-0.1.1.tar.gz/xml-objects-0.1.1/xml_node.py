"""Easy working with and searching through XML data"""

from xml.etree import ElementTree


class XMLNode:
    """A Node (or list of them) in an XML Dom."""
    def __init__(self, *elements):
        self.elements = elements
        self.tag = elements[0].tag

    @classmethod
    def from_file(cls, filename):
        tree = ElementTree.parse(filename)
        return cls(tree.getroot())

    @classmethod
    def from_string(cls, text):
        tree = ElementTree.fromstring(text)
        return cls(tree.getroot())

    def __getattr__(self, query):
        multi_children = []
        for element in self.elements:
            multi_children.extend(element.findall(query))
        if len(multi_children) == 0:
            raise AttributeError(f"{self.tag} has no child {query}")
        return XMLNode(*multi_children)

    def __str__(self):
        return f"<XMLNode tag={self.tag}>"

    def __iter__(self):
        return iter([XMLNode(element) for element in self.elements])

    def __str__(self):
        return f"<XMLNode tag={self.tag}, children={len(self.elements)}>"

    @property
    def value(self):
        if len(self.elements) == 1:
            return self.elements[0].text or None
        else:
            return [element.text or None for element in self.elements]

    @value.setter
    def value(self, new_val):
        for element in self.elements:
            element.text = new_val


if __name__ == "__main__":
    xml = XMLNode.from_file('sample.xml')
    print(xml.book.price.value)
    for book in xml.book:
        print(f"{book.title.value}, {book.author.value}, {book.price.value}")