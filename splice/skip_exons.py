#!/usr/bin/env python3

import argparse
from gtf import gtf_to_json


def exon_size(exon):
    """ Calculate the size of an exon

    The begin of an attribute in GTF is 1-based, and inclusive
    The end of an attribute in GTF is also inclusive.

    See https://www.ensembl.org/info/website/upload/gff.html

    For example, setting start-end to 1-2 describes two bases, the first and second base in the sequence
    """
    start = int(exon['start'])
    end = int(exon['end'])
    return end - start + 1


def usable(record):
    """ Helper function to determine if we can use a record

    We are only interested in protein coding exons.

    """
    return (record['feature'] == 'exon' and
            record['attribute']['transcript_biotype'] =='protein_coding')


def gtf_by_transcript(gtf):
    # Store the first exon we get
    for record in gtf_to_json(gtf):
        if usable(record):
            records = [record]
            transcript_id = record['attribute']['transcript_id']
            break

    # Then we parse the whole file, yielding the result every time we arrive at
    # a new transcript
    for record in gtf_to_json(args.gtf):
        if usable(record):
            # If we find a new transcript
            current_transcript = record['attribute']['transcript_id']
            if transcript_id !=  current_transcript:
                yield transcript_id, records
                transcript_id = current_transcript
                records = [record]
            else:
                records.append(record)
    # Once we are done parsing the entire file, yield the last records
    else:
        yield transcript_id, records


def skippable_exons(exons):
    """ Determine which exon(s) can be skipped

    For each exon (except the first and second, which cannot be skipped), we
    want to find the minimum number of exons which together have a size that
    can be divided by 3.
    >>> list(skippable_exons([30]))
    []
    >>> list(skippable_exons([30,30]))
    []
    >>> list(skippable_exons([30,30,30]))
    [[1]]
    >>> list(skippable_exons([30,30,30,30]))
    [[1], [2]]
    >>> list(skippable_exons([30,31,32,30]))
    [[1, 2]]
    >>> list(skippable_exons([30,32,32,30]))
    []

    """
    # If there are less than 3 exons, there is nothing to skip
    if len(exons) < 3:
        return []

    # We check every exon that isn't the first or the last
    for i in range(1,len(exons)):
        # Test every sub-sequence of exons, starting from the current exon
        for j in range(i+1, len(exons)):
            # Determine the total lenght of the exons we are considering
            total_length = sum(exons[i:j])
            if total_length%3 == 0:
                yield list(range(i,j))
                # Once we found the minimum number of exons to skip to stay in
                # frame (can be 1), we are not interested in skipping more
                break


def splice_site_to_bed(exon):
    """ Return the splice acceptor site for exon, in bed format

    We want to edit the highly conserved G in the splice acceptor site directly
    before the start of the exon.

    See Figure 1 of Gapinske2018: https://doi.org/10.1186/s13059-018-1482-5

    """
    chrom = exon['seqname']

    # gtf is 1 based, while bed is 0 based
    # And the splice acceptor site starts 2bp before the exon itself
    begin = int(exon['start']) - 2

    # The splice acceptor site is 5 bp, see reference above
    end = begin + 1

    # The name is the transcript name + the exon number
    attr = exon['attribute']
    ts_name = attr['transcript_id']
    exon_nr = attr['exon_number']
    name = f'{ts_name}:{exon_nr}'
    return (f'chr{chrom}', begin, end, name)


def main(args):
    # The splice sites for skippable exons, in bed format
    skip_sites = set()

    for transcript, exons in gtf_by_transcript(args.gtf):
        # Represent a transcript as a string of exon lenghts
        ts = [exon_size(exon) for exon in exons]

        for to_skip in skippable_exons(ts):
            # If there are too many exons to skip, continue
            if len(to_skip) > args.max_skip:
                continue
            # Add the splice sites in bed format to skip_sites
            for index in to_skip:
                skip_sites.add(splice_site_to_bed(exons[index]))

    # Print the skippable splice sites, in bed format. Using the default python
    # sort on tuples gives a valid sorting for bed files
    for region in sorted(skip_sites):
        print(*region, sep='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--gtf', type=argparse.FileType('r'), required=True)
    parser.add_argument('--max-skip', type=int, default=1,
                        help='maximum number of exons to skip at once')

    args = parser.parse_args()

    main(args)
