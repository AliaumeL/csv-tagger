# Python Comma Separated Value Annotator

[Libre Office Calc]: https://www.libreoffice.org/discover/calc/

<figure>
    <img src="csv-python-demo.svg" width="90%" />
    <caption>
    Illustrating the usage of the program on a sample
    CSV file.
    </caption>
</figure>

## Objectives

The goals are to be "on par" with the
spreadsheet system using [Libre Office Calc]
to annotate CSV files. In particular, the following
features are present:

1. One can decide how to import columns, specify
   the separator of the CSV file, and
   where the import should start (ignoring headers
   for instance).
2. One can rename columns, and decide 
   which ones are to be considered as
   dates, numbers, strings.
3. One can quit and resume the annotation at 
   any point in time.
4. Upon exit, a breif summary of the tags
   is provided.

## How to build

Dependencies are minimal. The script is built
using `click` and `pydantic`.

## How to run

If all dependencies are available in the current path,
the following command
should do the trick.

```bash
python3 -m py_csv_tagger.csv_tagger
```

There are two commands for the program. The first one, `new` takes as input a
CSV file. The second, `resume` takes as input a `.csvt` file that is a custom
format handled by `py-csv-tagger`.
