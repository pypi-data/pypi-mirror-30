from collections import OrderedDict
import json as _json
import pandas as pd
import click


# Consts

# Spaces intentional - malformed file format
VERSIONS = {
    'TLS 1.0': ' tls10Requests',
    'TLS 1.1': ' tls11Requests',
}

REQ_TOTAL = ' requests'
ACC_ID = ' Account ID'
SITE_ID = ' Site ID'
SITE_NAME = ' Site Name'

# Err msgs
NO_ACCOUNT_OR_SITE = 'Must specify either Account or Site ID.'
ACCOUNT_AND_SITE = 'Cannot specify both Account and Site ID. Specify one or the other.'
INVALID_PATH = 'Invalid path or file does not exist: {}'
UNKNOWN_ERR = 'Unknown error'
DOES_NOT_EXIST = 'Could not find {} {} in file.'
NO_OUTPUT = 'Can\'t pass --silent without --json. Exiting.'

# /Consts


class TlsExtractorException(Exception):
    """TLSX base exception class"""

    def __init__(self, message='TLS Extractor Exception'):
        self._message = message

    def __str__(self):
        return self._message


def write_json(_id, breakdown):
    with open(_id + '.json', 'w') as file:
        file.write(_json.dumps(breakdown, indent=4))


def extract_account_breakdown(df, account, silent, json):
    acc_df = df[df[ACC_ID] == int(account)]
    if acc_df.empty:
        raise TlsExtractorException(DOES_NOT_EXIST.format('account', account))

    breakdown = []

    for row in acc_df.iterrows():
        series = row[1]
        site_data = OrderedDict()

        site_data['Site Name'] = series[SITE_NAME]
        site_data['Total Requests'] = series[REQ_TOTAL]

        for ver in VERSIONS.keys():
            site_data[ver] = series[VERSIONS.get(ver)]
        breakdown.append(site_data)

    if not silent:
        print('### Account {} TLS breakdown ###\r\n'.format(account))
        for site in breakdown:
            for k, v in site.items():
                print('{}: {}'.format(k, v))
            print('\r\n')
    if json:
        write_json(account, breakdown)


def extract_site_breakdown(df, site, silent, json):
    site_df = df[df[SITE_ID.strip()] == int(site)]
    if site_df.empty:
        raise TlsExtractorException(DOES_NOT_EXIST.format('site', site))

    # Convert dataframe to series
    series = site_df.iloc[0, :]

    breakdown = OrderedDict()
    breakdown['Site Name'] = series[SITE_NAME]
    breakdown['Account ID'] = series[ACC_ID]
    breakdown['Total Requests'] = series[REQ_TOTAL]

    for ver in VERSIONS.keys():
        breakdown[ver] = series[VERSIONS.get(ver)]

    if not silent:
        print('### {} TLS breakdown ###\r\n'.format(series[SITE_NAME]))
        for k, v in breakdown.items():
            print('{}: {}'.format(k, v))
    if json:
        write_json(site, breakdown)


@click.command()
@click.option('-a', '--account', help='Account ID to extract TLS breakdown for.\n'
                                      'Will extract breakdown for all sites under this Account ID')
@click.option('-s', '--site', help='Site ID to extract TLS breakdown for')
@click.option('-f', '--file', required=True, help='TLS file in csv format to extract breakdown from')
@click.option('--json', is_flag=True, help='Output to JSON file')
@click.option('--silent', is_flag=True, help='Do not print anything to sdout')
def main(file, account, site, json, silent):
    """
    Pass -a, --account [Account ID] to extract breakdown for all sites of the account.

    Pass -s, --site [Site ID] to extract break down for a specific site.
    Cannot use both at the same time. ¯\_(ツ)_/¯

    Pipe the output to a file using '> file.txt' following the command or use --json to get a JSON formatted file.

    Usage examples:

    `tlsx -f my_tls_file.csv --account 1234567`

    `tlsx -f another_file.csv --site 987654`
    """

    # Argument parsing
    if silent and not json:
        raise TlsExtractorException(NO_OUTPUT)

    if account and site:
        raise TlsExtractorException(ACCOUNT_AND_SITE)

    if not account and not site:
        raise TlsExtractorException(NO_ACCOUNT_OR_SITE)

    try:
        df = pd.read_csv(file, encoding='latin1')
    except FileNotFoundError:
        raise TlsExtractorException(INVALID_PATH.format(file))

    # Handle account
    if account:
        extract_account_breakdown(df, account, silent, json)

    # Handle site
    else:
        extract_site_breakdown(df, site, silent, json)
