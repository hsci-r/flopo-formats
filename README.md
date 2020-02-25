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
mkdir -p data/work/webanno
mkdir -p data/work/webanno-annotated
flopo-convert -f csv -t webanno-tsv -i data/final/kiky.conll.csv -O data/work/webanno/
flopo-annotate -a \
	NamedEntity:data/final/kiky.ner.csv \
	Quote:data/final/kiky.quotes.csv \
	IQuote:data/final/kiky.iquotes.csv \
	Metaphor:data/final/kiky.metaphors.csv \
	Hedging:data/final/kiky.hedging.csv \
	-I data/work/webanno/ -O data/work/webanno-annotated/
flopo-package \
	-I data/work/webanno-annotated/ \
	-t data/raw/webanno-project-template.json \
	-o data/final/kiky.zip \
	-n 'Case KIKY'
```

The commands are described below. Furthermore, each command has a `--help`
option, which will print detailed usage information.

## `flopo-annotate`

This tool is used to merge the annotations from CSV files into an existing
corpus of WebAnno-TSV files.

### Arguments

- `-a`, `--annotations` -- a list of annotations to include, each having the
  format: `LAYER:FILE`, where `LAYER` is the name of the layer (for example
  'Hedging') and `FILE` is a CSV file.
- `-I`, `--input-dir` -- The directory containing the corpus (as WebAnno TSV
  files).
- `-O`, `--output-dir` -- The directory into which the annotated TSV files will
  be saved.

### Examples

```
flopo-annotate -a \
	NamedEntity:kiky.ner.csv \
	Quote:kiky.quotes.csv \
	Metaphor:kiky.metaphors.csv \
	Hedging:kiky.hedging.csv \
	-I webanno/ -O webanno-annotated/
```

Add the annotations of named entities, quotes, metaphors and hedging to all TSV
files in the folder `webanno`. Save the results in the folder
`webanno-annotated`.

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
- `-d`, `--delimiter` -- the field delimiter for the output format (default:
  comma). If you want to do some further processing (e.g. with `cut` or `awk`),
  it is useful to set it to Tab.
- `--doc-id` -- the document ID (optional; default: filename without `.tsv`
  suffix)

### Examples


Print out the annotations from the layer `Metaphor` to a CSV file:

```
flopo-export -a Metaphor -I webanno/ -o metaphors.csv
```

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

## `flopo-eval`

Compare annotations to a gold standard.

### Arguments

- `-i`, `--input-file` -- CSV file containing the annotations to evaluate,
- `-g`, `--gs-file` -- CSV file containing the gold standard annotation,
- `-c`, `--corpus-file` -- corpus file (CoNLL format),
- `-r`, `--results-format` -- results format: `short` - print only evaluation
  measures, `long` - print results for each sentence, `csv` - output a CSV
  suitable for more detailed evaluation.

### Examples

```
flopo-eval \
	-c kiky.conll.csv  -i kiky.conll.quotes.csv \
	-g quotes.aharju.csv -r csv
```

## `flopo-package`

Package a corpus of WebAnno files as a project (zip file) ready to import to
WebAnno.

### Arguments

- `-I`, `--input-dir` -- the directory containing WebAnno-TSV files,
- `-t`, `--template-file` -- a JSON file containing a template of the project
  metadata (in a format expected by WebAnno),
- `-n`, `--name` -- the project name,
- `-o`, `--output-file` -- the resulting zip file (default: `NAME.zip`).

### Examples

```
flopo-package \
	-I data/work/webanno/ \
	-t data/raw/webanno-project-template.json \
	-o kiky.zip -n 'Case KIKY'
```

