# Installation

```
python3 setup.py install
```

## Local installation

For a local installation for the current user, make sure the directory
`~/.local/lib/python3.x` exists (where *x* is the minor version number of your
Python install) and run:

```
python3 setup.py install --prefix=~/.local
```

# Commands

The package provides commands for manipulating FLOPO data. The usual pipeline
consists of calls like this:
```
flopo-convert -f csv -t webanno-tsv -i kiky.conll.csv -O webanno/
flopo-finer -i kiky.conll.csv -o kiky.ner.csv
flopo-annotate -a \
	NamedEntity:kiky.ner.csv \
	Quote:kiky.quotes.csv \
	Metaphor:kiky.metaphors.csv \
	Hedging:kiky.hedging.csv \
	-- webanno/
```

The following CLI tools are currently provided:
- `flopo-annotate`: Add annotations provided as CSV files into a corpus
  of WebAnno TSV documents.
- `flopo-convert`: Convert between different file formats used in FLOPO.
- `flopo-finer`: Tag named entities using FINER.

Each tool has a `--help` option, which will print detailed usage information.

