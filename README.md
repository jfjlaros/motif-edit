PAS analysis
============

Reference data
--------------

Retrieved on 2020-09-26.

    mkdir input
    cd input
    wget https://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz
    wget https://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.chrom.sizes
    wget ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_35/gencode.v35.polyAs.gff3.gz
    gunzip hg38.fa.gz
    zgrep 'polyA_signal' gencode.v35.polyAs.gff3.gz | cut -f 1,4,5,7 > hg38_PAS.bed

Analysis
--------

Load the appropriate virtual environment and run the analysis.

    workon fastools
    make
