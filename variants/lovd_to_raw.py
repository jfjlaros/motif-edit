from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from csv import DictReader, Sniffer

from mutalyzer_hgvs_parser import to_model
from mutalyzer_hgvs_parser.exceptions import UnexpectedCharacter, UnexpectedEnd


def lovd_to_bed(input_handle, output_handle, ref, alt):
    dialect = Sniffer().sniff(input_handle.read(1024))
    input_handle.seek(0)
    for record in DictReader(
            filter(lambda x: x[0] != '#', input_handle), dialect=dialect):
        chrom = 'chr{}'.format(record['{{chromosome}}'])
        try:
            model = to_model('{}:{}'.format(
                chrom, record['{{VariantOnGenome/DNA/hg38}}']))
        except (UnexpectedCharacter, UnexpectedEnd):
            continue

        for variant in model['variants']:
            if (
                    variant['type'] == 'substitution' and
                    variant['deleted'][0]['sequence'] == ref and
                    variant['inserted'][0]['sequence'] == alt):
                output_handle.write('{}\t{}\t{}\n'.format(
                    chrom, variant['location']['position'] - 1,
                    variant['location']['position']))


def main():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description='', epilog='')
    parser.add_argument('input_handle', metavar='INPUT', type=FileType('r'),
        help='file name')
    parser.add_argument('-o', dest='output_handle', metavar='OUTPUT',
        type=FileType('w'), default='-', help='file name')
    parser.add_argument('ref', metavar='REF', type=str, help='reference')
    parser.add_argument('alt', metavar='ALT', type=str, help='alternative')

    args = parser.parse_args()

    lovd_to_bed(**{k: v for k, v in vars(args).items()})


if __name__ == '__main__':
    main()
