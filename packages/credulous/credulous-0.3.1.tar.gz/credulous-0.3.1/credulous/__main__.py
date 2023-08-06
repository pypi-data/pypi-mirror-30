from __future__ import absolute_import

import argparse
from credulous import credulous

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s',
        '--secret',
        required = True
    )

    parser.add_argument(
        '-o',
        '--output'
    )

    parser.add_argument(
        '-c',
        '--credentials-format',
        action = 'store_true'
    )

    parser.add_argument(
        'scopes'
    )

    args = parser.parse_args()

    path_to_secret = args.secret
    path_to_scopes = args.scopes

    if args.output:
        path_to_output = args.output
    else:
        path_to_output = path_to_secret

    if args.credentials_format:
        format_function = credulous.format_as_credentials
    else:
        format_function = credulous.format_as_client_secret

    credulous.Credulous(
        path_to_secret,
        path_to_scopes,
        path_to_output,
        format_function
    ).authenticate()

if __name__ == '__main__':
    main()
