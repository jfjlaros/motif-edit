#!/usr/bin/env python3

import argparse
from gtf import gtf_to_json
from gtf import gtf_to_csv
from gtf import gtf_header


def main(args):
    # To flatten the entire GTF file, we need to know all of the possible
    # fields in the 'attribute' column. Therefore, we have to parse the entire
    # GTF file twice. Unless we want to keep the whole thing in memory, which
    # is not feasable.
    attributes = set()
    for record in gtf_to_json(args.gtf):
        attributes.update(list(record['attribute']))

    attributes = sorted(attributes)

    # We expand the 'attribute' fields
    header = [x for x in gtf_header if x != 'attribute']

    print(*header + attributes, sep=',')
    # Now we can parse the GTF file again, and write every line
    args.gtf.seek(0)
    for record in gtf_to_json(args.gtf):
        print(gtf_to_csv(record, attributes))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--gtf', type=argparse.FileType('r'), required=True)

    args = parser.parse_args()

    main(args)
