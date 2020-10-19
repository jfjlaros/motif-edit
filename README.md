# Motif editing

We present a procedure that searches for the locations of a motif in a
reference sequence and intersects these locations with a list of genomic
feature locations.

Originally, this was designed for finding editable poly(A) signals.

## Installation

The dependencies can be installed with the following commands.

    sudo apt install awk bedtools gzip make wget
    sudo pip install fastools

Alternatively, `fastools` can be installed in a virtual environment.

    mkvirtualenv fastools
    pip install fastools

The source can be retrieved with the following command.

    git clone https://github.com/jfjlaros/motif-edit.git
    cd motif-edit

## Analysis

The *motif* can be modified by editing `motifs.tsv`. This file contains four
tab separated lines.

| name | description
|:--   |:--
| `+f` | Forward motif on the forward strand.
| `-r` | Reverse complement motif on the reverse complement strand.
| `+r` | Forward motif on the reverse complement strand.
| `-f` | Reverse motif on the forward strand.

For the format of the motifs, see the page on
[extended regular expressions](https://docs.python.org/3/library/re.html).

The analysis is executed using the `make` command. If no reference data is
found, it will be downloaded on the first run.

    make

Output files can be removed as follows.

    make clean

All files, including the downloaded reference data  can be removed as follows.

    make distclean

If `fastools` is installed in a virtual environment, this environment must be
activated before starting the analysis.

    workon fastools
    make

## Configuration

Configuration is done by setting variables at the top of the `Makefile`.

The build version is specified by setting the `BUILD` variable. When this
setting is changed, it is probably necessary to change `ANNOTATION` and
`ANNOTAION_URL` as well.

A feature is selected by setting the `FILTER` variable. The following command
can be used to retrieve a list of features.

    make features

To get a list of reference data locations, the following command can be used.

    make reference
