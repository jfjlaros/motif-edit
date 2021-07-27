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
            if transcript_name !=  record['attribute']['transcript_name']:
                yield transcript_name, records
                transcript_name = record['attribute']['transcript_name']
                records = [record]
            else:
                records.append(record)
    # Once we are done parsing the entire file, yield the last records
    else:
        yield transcript_name, records

import sys
def main(args):
    for transcript, exons in gtf_by_transcript(args.gtf):
        print(transcript, file=sys.stderr)
        print(json.dumps(exons, indent=True))

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
