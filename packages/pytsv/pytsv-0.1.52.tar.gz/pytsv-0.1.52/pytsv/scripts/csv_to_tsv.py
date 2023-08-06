import csv

import click

import sys
import pyanyzip.core

from typing import List

from pytsv.pytsv import TsvWriter, CHECK_NUM_FIELDS


@click.command()
@click.option(
    '--input-file',
    required=True,
    type=str,
    help="input file",
    show_default=True,
)
@click.option(
    '--output-file',
    required=True,
    type=str,
    help="output file",
    show_default=True,
)
@click.option(
    '--set-max',
    required=False,
    default=True,
    type=bool,
    help="do you want to unset the limit on csv fields (good for large fielded csv files)",
    show_default=True,
)
@click.option(
    '--replace-tabs-with-spaces',
    required=False,
    default=True,
    type=bool,
    help="do you want to replace tabs with spaces?",
    show_default=True,
)
@click.option(
    '--check-num_fields',
    required=False,
    default=CHECK_NUM_FIELDS,
    type=bool,
    help="check that all lines have the same number of fields?",
    show_default=True,
)
def main(
        input_file,
        output_file,
        set_max,
        replace_tabs_with_spaces,
        check_num_fields,
):
    # type: (str, str, bool, bool, bool) -> None
    """ This script converts a CSV to a TSV file """
    if set_max:
        csv.field_size_limit(sys.maxsize)
    with pyanyzip.core.open(input_file, "rt") as input_file_handle:
        csv_reader = csv.reader(input_file_handle)
        with TsvWriter(
            filename=output_file,
            check_num_fields=check_num_fields,
        ) as output_file_handle:
            for row in csv_reader:  # type: List[str]
                if replace_tabs_with_spaces:
                    for i, item in enumerate(row):
                        row[i] = row[i].replace("\t", " ")
                output_file_handle.write(row)


if __name__ == '__main__':
    main()
