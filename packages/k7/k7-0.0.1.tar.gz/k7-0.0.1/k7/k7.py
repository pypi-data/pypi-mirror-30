"""
This module provides methods to parse and manipulate K7 files
"""

import json
import pandas as pd

REQUIRED_HEADER_FIELDS = [
    'start_date',
    'stop_date',
    'site',
]
REQUIRED_DATA_FIELDS = [
    'datetime',
    'src',
    'dst',
    'channel',
    'mean_rssi',
    'pdr',
    'transaction_id'
]

__version__ = "0.0.1"

def read(file_path):
    # read header
    with open(file_path, 'r') as f:
        header = json.loads(f.readline())

    # read data
    df = pd.read_csv(file_path,
                     parse_dates = ['datetime'],
                     index_col = [0],  # make datetime column as index
                     skiprows=1,
                     )
    return header, df

def write(output_file_path, header, data):
    with open(output_file_path, 'w') as f:
        # write header
        json.dump(header, f)
        f.write('\n')

        # write data
        data.to_csv(f)

def check(file_path):
    """
    Check if k7 format is respected
    :return:
    """

    header, df = read(file_path)

    for required_header in REQUIRED_HEADER_FIELDS:
        if required_header not in header:
            print "Header {0} missing".format(required_header)

if __name__ == "__main__":
    import argparse

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--check",
                        help="check the dataset format",
                        type=str,
                        dest='file_to_check',
                        )
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + __version__)
    args = parser.parse_args()

    # run corresponding method
    if hasattr(args, "file_to_check"):
        check(args.file_to_check)
    else:
        print "Command {0} does not exits."
