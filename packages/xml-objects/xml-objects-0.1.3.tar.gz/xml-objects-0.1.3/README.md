# XML Objects

Makes managing XML a lot easier by making an XML document look like nested Python objects.

## Installing

Install via `pip`:

    pip install xml-objects

## Usage

See [sample.xml](sample.xml) for the structure used in these examples.  Taken unashamedly from Microsoft's [Sample XML](https://msdn.microsoft.com/en-us/library/ms762271.aspx).  The results of the code below can be seen by running [`xml_node.py`](xml_node.py) directly.

```python
xml = XMLNode.from_file('sample.xml')
print(xml.book.price)
for book in xml.book:
    print(f"{book.title.value}, {book.author.value}, {book.price.value}")
```

Which will output:

```
PS [34] master -> python .\xml_node.py

['44.95', '5.95', '5.95', '5.95', '5.95', '4.95', '4.95', '4.95', '6.95', '36.95', '36.95', '49.95']
XML Developer's Guide, Gambardella, Matthew, 44.95
Midnight Rain, Ralls, Kim, 5.95
Maeve Ascendant, Corets, Eva, 5.95
Oberon's Legacy, Corets, Eva, 5.95
The Sundered Grail, Corets, Eva, 5.95
Lover Birds, Randall, Cynthia, 4.95
Splish Splash, Thurman, Paula, 4.95
Creepy Crawlies, Knorr, Stefan, 4.95
Paradox Lost, Kress, Peter, 6.95
Microsoft .NET: The Programming Bible, O'Brien, Tim, 36.95
MSXML3: A Comprehensive Guide, O'Brien, Tim, 36.95
Visual Studio 7: A Comprehensive Guide, Galos, Mike, 49.95
```

## Future Ideas

 - Script to drop into a shell with the functionality of XMLNode.  Optionally, with an argument to pre-load an XML file.
 - The `__str__` method should probably print out available child-nodes for ease of exploration.
 - Open from URL?

## Contributing

I'd love to have people contribute.  Feel free to open a pull request and we'll talk about it!

## Code of Conduct

See the [Code of Conduct](CODE_OF_CONDUCT.md).
