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

The commands are described below. Furthermore, each command has a `--help`
option, which will print detailed usage information.

## `flopo-annotate`

This tool is used to merge the annotations from CSV files into an existing
corpus of WebAnno-TSV files.

### Arguments

- `-a`, `--annotations` -- a list of annotations to include, each having the
  format: `LAYER:FILE`, where `LAYER` is the name of the layer (for example
  'Hedging') and `FILE` is a CSV file. Terminate the list with `--`.
- `corpus_dir` -- The directory containing the corpus (as WebAnno TSV files).
  CAUTION: the files will be overwritten.

### Examples

```
flopo-annotate -a \
	NamedEntity:kiky.ner.csv \
	Quote:kiky.quotes.csv \
	Metaphor:kiky.metaphors.csv \
	Hedging:kiky.hedging.csv \
	-- webanno/
```

Add the annotations of named entities, quotes, metaphors and hedging to all TSV
files in the folder `webanno`.

## `flopo-convert`

Convert between different file formats used in FLOPO.

### Arguments

- `-f`, `--from` -- input format (currently `csv` or `webanno-tsv`),
- `-t`, `--to` -- output format (currently `webanno-tsv` or `prolog`), use
  `flopo-export` to convert WebAnno files back to CSV,
- `-i`, `--input-file`,
- `-I`, `--input-dir` -- currently not used,
- `-o`, `--output-file`,
- `-O`, `--output-dir` -- use for conversion from CSV to WebAnno.

### Examples

```
flopo-convert -f csv -t webanno-tsv -i kiky.conll.csv -O webanno/
```

Convert a whole corpus from CSV format (CoNLL columns) to WebAnno-TSV files and
save them in the folder `webanno`.

```
flopo-convert -f webanno-tsv -t prolog -i 99860144 -o 99860144.pl
```

Convert a single TSV file to Prolog.

## `flopo-export`

Export the annotations from WebAnno files as text or CSV.

### Arguments

- `-a`, `--annotation` -- the annotation layer to export.
- `-i`, `--input-file` -- a single WebAnno TSV file.
- `-I`, `--input-dir` -- alternatively, you may supply a directory containing
  WebAnno TSV files.
- `-o`, `--output-file` -- output file; if none or `-` given, standard output
  is used.
- `-t`, `--text` -- if set, the last column of the output will contain the full
  text of annotation spans.
- `-d`, `--delimiter` -- the field delimiter for the output format (default:
  comma). If you want to do some further processing (e.g. with `cut` or `awk`),
  it is useful to set it to Tab.

### Examples

```
flopo-export -a Metaphor -I webanno/ -o metaphors.csv
```

Prints out the annotations from the layer `Metaphor` to a CSV file.

```
$ flopo-export -a IQuote -i 99860144 -t -d '       ' | cut -f 6,8
author  text
Fjäder  Hallitus on pitänyt aikaisemminkin esillä toissapäivänä esittelemäänsä kilpailukykyehdotusta, kertoo Akavan puheenjohtaja Sture Fjäder STT:lle.
hallitus        se ryhtyy valmistelemaan omaa malliaan kilpailukyvyn parantamiseksi
Hallitus        se ei aikaisemmin kerrotusta poiketen pienennäkään sunnuntai- ja ylityökorvauksia
STTK:n_puheenjohtajan_Antti_Palolan     malli on ainakin osittain sama kuin 20. elokuuta.
Työmarkkinajohtajat     neuvottelut kestävät joitakin viikkoja
Lyly    Osapuolilla ovat neuvotteluesitykset pöydällä ja niistä lähdetään vääntämään, SAK:n puheenjohtaja Lauri Lyly sanoi.
```

Shows the indirect quotes from a single document.

## `flopo-finer`

Tag named entities using FINER.

### Arguments

- `-i`, `--input-file` -- CSV file containing a corpus to annotate,
- `-o`, `--output-file` -- CSV file to save FINER annotations,
- `--remote` -- use a remote FINER instance; its URL is currently hardcoded to
  `https://finer-flopo.rahtiapp.fi`.

### Examples

```
flopo-finer -i kiky.conll.csv -o kiky.ner.csv
```

Annotate the corpus using local FINER.

```
flopo-finer --remote -i kiky.conll.csv -o kiky.ner.csv
```

The same using remote FINER.

