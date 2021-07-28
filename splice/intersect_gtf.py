#!/usr/bin/env python3

import argparse
from gtf import gtf_to_json
from gtf import json_to_gtf
from gtf import usable


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


def read_bedfile(handle):
    """ Read the bed file

    We are only interested in the transcript_id and exon_nr
    """
    include = set()
    for line in handle:
        name = line.strip('\n').split('\t')[3]
        transcript_id, exon_nr = name.split(':')
        include.add((transcript_id, exon_nr))
    return include


def print_exon_gtf(record):
    import json
    print(json.dumps(record, indent=True))
    print(json_to_gtf(record))
    exit()

def main(args):
    # Read the transcripts, exon_nrs from the bed file
    include = read_bedfile(args.bed)


    # Store all editable exons, we cannot write them to
    editable_exons = list()
    for record in gtf_to_json(args.gtf):
        if usable(record):
            transcript_id = record['attribute']['transcript_id']
            exon_nr = record['attribute']['exon_number']
            if (transcript_id, exon_nr) in include:
                print_exon_gtf(record)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--gtf', type=argparse.FileType('r'), required=True)
    parser.add_argument('--bed', type=argparse.FileType('r'), required=True)

    args = parser.parse_args()

    main(args)
