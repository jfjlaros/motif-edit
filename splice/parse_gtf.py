#!/usr/bin/env python3

import argparse
import json


def main(args):
    for record in parse_gtf(args.gtf):
        print(json.dumps(record, indent=True))
        exit()

def parse_attribute(attribute):
    """ attribute - A semicolon-separated list of tag-value pairs """
    attributes = dict()
    for attr in attribute.split(';')[:-1]:
        #print(attr)
        #print(attr.strip().split(' '))
        #print('=='*40)
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
