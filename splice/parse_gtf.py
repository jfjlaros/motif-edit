#!/usr/bin/env python3

import argparse
import json


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

def gtf_by_transcript(gtf):
    # Store the first exon we get
    for record in parse_gtf(gtf):
        if record['feature'] == 'exon':
            records = [record]
            transcript_name = record['attribute']['transcript_name']
            break

    # Then we parse the whole file, yielding the result every time we arrive at
    # a new transcript
    for record in parse_gtf(args.gtf):
        if record['feature'] == 'exon':
            # If we find a new transcript
            current_transcript = record['attribute'].get('transcript_name')
            if transcript_name !=  current_transcript:
                yield transcript_name, records
                transcript_name = current_transcript
                records = [record]
            else:
                records.append(record)
    # Once we are done parsing the entire file, yield the last records
    else:
        yield transcript_name, records


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


    We assume the 5-bp motif as shown in Figure one of https://doi.org/10.1186/s13059-018-1482-5

    """
    #print(json.dumps(exon, indent=True))
    chrom = exon['seqname']

    # gtf is 1 based, while bed is 0 based
    # And the splice acceptor site starts 2bp before the exon itself
    begin = int(exon['start']) - 3

    # The splice acceptor site is 5 bp, see reference above
    end = begin + 5

    # The name is the transcript name + the exon number
    attr = exon['attribute']
    name = f'{attr["transcript_name"]}:{attr["exon_number"]}'
    return (chrom, begin, end, name)


def main(args):
    for transcript, exons in gtf_by_transcript(args.gtf):
        # For debuggin, we only look at DMT
        if transcript != 'DMD-203':
            continue

        # Represent a transcript as a string of exon lenghts
        ts = [exon_size(exon) for exon in exons]
        for to_skip in skippable_exons(ts):
            for index in to_skip:
                print(splice_site_to_bed(exons[index]))
        exit()
        for exon in exons:
            attr = exon['attribute']
            number = attr.get('exon_number')
            size = exon_size(exon)
            assert size > 0
            print(f'{transcript}:{number}\t{size}\t{size%3}')
        print('-'*20)
        #print(json.dumps(exons, indent=True))

def parse_attribute(attribute):
    """ attribute - A semicolon-separated list of tag-value pairs """
    attributes = dict()
    for attr in attribute.split(';')[:-1]:
        key, *value = attr.strip().split(' ')
        attributes[key] = ' '.join(val.replace('"','') for val in value)
    return attributes


def parse_gtf(gtf_handle):
    # See https://www.ensembl.org/info/website/upload/gff.html
    gtf_header = 'seqname source feature start end score strand frame attribute'.split()

    # Skip the headers
    line = next(gtf_handle)
    while line.startswith('#'):
        line = next(gtf_handle)
        continue

    for line in gtf_handle:
        spline = line.strip('\n').split('\t')
        record = {k:v for k, v in zip(gtf_header, spline)}
        record['attribute'] = parse_attribute(record['attribute'])
        yield record


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--gtf', type=argparse.FileType('r'), required=True)

    args = parser.parse_args()

    main(args)
