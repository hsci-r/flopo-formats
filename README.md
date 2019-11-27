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
flopo-finer -i kiky.conll.csv -o kiky.conll.ner.csv
flopo-annotate -a \
	NamedEntity:kiky.ner.csv \
	Quote:kiky.quotes.csv \
	Metaphor:kiky.metaphors.csv \
	Hedging:kiky.hedging.csv \
	-- webanno/
```

## `flopo-convert`

TODO

## `flopo-finer`

TODO

## `flopo-annotate`

TODO
