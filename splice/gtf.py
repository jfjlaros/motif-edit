#!/usr/bin/env python3

import argparse


def parse_attribute(attribute):
    """ attribute - A semicolon-separated list of tag-value pairs """
    attributes = dict()
    for attr in attribute.split(';')[:-1]:
        key, *value = attr.strip().split(' ')
        attributes[key] = ' '.join(val.replace('"','') for val in value)
    return attributes


def gtf_to_json(gtf_handle):
    """ Parse a GTF file, and yield the records one by one """
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
