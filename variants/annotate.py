from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from binning import containing_bins
from csv import DictReader
from mysql import connector
from requests import request, Session

from sys import stdout


def get_token(email, password):
    api_host = 'https://www.disgenet.org/api'
    s = Session()

    payload = {'email': email, 'password': password}
    r = s.post(f'{api_host}/auth/', data=payload)
    if (r.status_code == 200):
        return r.json()['token']

def annotate(input_handle, output_handle, ref, alt, DISGENET_USER, DISGENET_PASSWORD):
    connection = connector.connect(
        user='genome', host='genome-euro-mysql.soe.ucsc.edu', port=3306,
        database='hg38')
    cursor = connection.cursor()

    input_handle.readline()
    reader = DictReader(
        input_handle, fieldnames=['chrom', 'start', 'end'], delimiter='\t')
    output_handle.write('{}\n'.format('\t'.join([
        'chrom', 'start', 'end', 'ref', 'alt', 'alleles', 'frequencies',
        'submitterCount', 'transcripts', 'genes', 'phenotype'])))

    # Get the disgenet token
    token = get_token(DISGENET_USER, DISGENET_PASSWORD)

    session = Session()
    session.headers.update({'Authorization': f'Bearer {token}'})

    for line in reader:
        bins = containing_bins(int(line['start']))
        query = ('SELECT name, name2 from refGene WHERE ' +
                 'chrom = "{0}" AND bin IN ({1}) AND ' +
                 'txStart <= {2} AND txEnd >= {2}').format(
            line['chrom'], ', '.join(map(str, bins)), line['start'])
        cursor.execute(query)
        names = list(map(set, (list(zip(*cursor))))) or [set([]), set([])]

        diseases = []
        for name in names[1]:
            response = session.get(f'https://www.disgenet.org/api/gda/gene/{name}')
            if response.ok:
                diseases += [x['disease_name'] for x in response.json()]

        # Fetch the alleles and allele frequencies
        query = ('SELECT alleles, alleleFreqs FROM snp151 WHERE ' +
                 'chrom = "{}" AND bin IN ({}) AND chromStart = {}').format(
            line['chrom'], ', '.join(map(str, bins)), line['start'])
        cursor.execute(query)
        result = list(map(
            lambda x: ';'.join(map(lambda y: y.decode().strip(','), x)),
            zip(*cursor))) or ['', '']

        # Fetch the submitter counts:
        # submitterCount	Number of distinct submitter handles for submitted SNPs for this ref SNP
        query = ('SELECT submitterCount FROM snp151 WHERE ' +
                 'chrom = "{}" AND bin IN ({}) AND chromStart = {}').format(
            line['chrom'], ', '.join(map(str, bins)), line['start'])
        cursor.execute(query)

        try:
            submitterCount = list(cursor)[0][0]
        except IndexError:
            submitterCount = ''

        output_handle.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
            '\t'.join(line.values()),
            ref, alt,
            '\t'.join(result),
            submitterCount,
            '\t'.join(map(lambda x: ','.join(x), names)),
            ';'.join(diseases)))

    cursor.close()
    connection.close()


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
    parser.add_argument('DISGENET_USER', type=str, help='username for disgenet')
    parser.add_argument('DISGENET_PASSWORD', type=str, help='password for disgenet')

    args = parser.parse_args()

    annotate(**{k: v for k, v in vars(args).items()})


if __name__ == '__main__':
    main()
