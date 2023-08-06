# csvgather

Utility for gathering multiple character-separated value files and joining into
a single matrix. Similar to [csvjoin](http://csvkit.readthedocs.io/en/latest/scripts/csvjoin.html)
from the [csvkit](http://csvkit.readthedocs.io) package, or the `join` function
of [csvtk](bioinf.shenwei.me/csvtk), except allows column headers to be renamed
based on the filename. This is an extremely common operation in, e.g.
bioinformatic analyses, when the same utility, which produces a file with static
headers, is produced for many files, differing only in some portion of the
filename.

For example, the RNA-Seq gene expression quantification tool
[kallisto](https://pachterlab.github.io/kallisto/about) produces a directory that
contains a file that is always named `abundance.tsv`, which has columns

```
target_id length eff_length est_counts tpm
```

To differentiate between samples, the directory is often named to include the
sample name, e.g. `sample_A__kallisto_counts/abundance.tsv`. Downstream analysis
steps often require the `est_counts` columns from many samples files to be
concatenated into a single matrix file. A simple join operation on the first
field of these files would produce a file with identical column names, making
such operations useless. This utility enables field-specific name transforms
based on input file. For example:

```
csvgather -j 0 -f est_counts -t "s:est_counts:{dir}:" -t "s:__kallisto_counts::" sample_*__kallisto_counts/abundance.tsv
```

This command joins all of the `abundance.tsv` files on the first column value,
selects only the columns `est_counts` from each file, and transforms the column
name of each column to include the directory name of the corresponding file, and
then transforming again to remove the `__kallisto_counts` part, leaving only the
sample name.

Maybe I'll try to integrate this utility into csvkit one day.

## Installation

You can install using `pip`:

```
pip install csvgather
```

## Usage

```
Usage: csvgather.py [options] [-j PATT]... [-f PATT]... [-t STR]... <csv_fn>...

Options:
  -h --help               This helpful help help help help is a weird word
  -d STR --delimiter=STR  Character(s) to use as the delimiter in the output,
                          can be multiple characters [default:  ]
  -o PATH --output=PATH   Output to file [default: stdout]
  -j COL --join=COL       Column(s) to join on. Can take one of four forms:
                            - 0-based integer indicating column index, can be
                              negative to index from the end of the columns
                            - a half closed interval of 0-based integers to
                              specify a range of columns (e.g. 0:4 or 0:-1)
                            - a regular expression that will use any columns it
                              matches as the join columns
                            - a pair of regular expressions to specify a range
                              of columns (e.g. geneName:strand will start with
                              the column geneName and end with column strand)
                          If more than one column matches, then a warning is
                          issued but the join continues on the aggregate of the
                          columns. ':' or special regular expression characters
                          (e.g. +, *, [, ], etc) in column names must be
                          wrapped in [], e.g. '[:]'. Can be specified multiple
                          times, in which case all selected columns are unioned
                          together [default: 0]
  -f COL --field=COL      Column(s) to select fields for concatenation. Uses
                          the same format as -j option. May be specified
                          multiple times and any matching columns will be
                          included. Column selection occurs before application
                          of transformations (-t). Joined columns are not
                          included in the field match [default: .]
  -t STR --transform=STR  A string of the form "s:patt:repl:[gi]" to apply to
                          every column name. The special strings {path}, {dir},
                          {fn}, and {basename} can be used in the repl string to
                          refer to the full path, parent directory name, file
                          name, and filename without extension (i.e. [.][^.]*$)
                          removed. May be specified multiple times, in which
                          case the transformations will be performed
                          sequentially in the order specified on the command
                          line [default: s:.:.:]
  --join-type=STR         Type of join, one of 'outer', 'inner', or 'left'.
                          outer will create a row for every distinct value in
                          the -j column(s), inner will report only rows that
                          are found in all files, and left will join files from
                          left to right [default: outer]
  --empty-val=VAL         The value to use when an outer or left join does not
                          find a corresponding row in a file [default: ]
  --comment=CHARS         Characters to be considered comments in input files
                          and will be skipped. Can be any number of characters
                          e.g. #@- [default: #]

```
