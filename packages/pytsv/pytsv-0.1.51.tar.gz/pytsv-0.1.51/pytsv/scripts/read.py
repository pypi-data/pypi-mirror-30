from typing import List

import click
import tqdm

from pytsv.pytsv import TsvReader


@click.command()
@click.option(
    '--progress',
    required=False,
    default=True,
    type=bool,
    help="show progress",
    show_default=True,
)
@click.argument(
    'input-files',
    nargs=-1,
    required=True,
)
def main(
        progress,
        input_files,
):
    # type: (bool, List[str]) -> None
    """ Read tsv files as plainly as possible """
    for input_file in input_files:
        with TsvReader(filename=input_file) as input_file_handle:
            if progress:
                input_file_handle = tqdm.tqdm(input_file_handle, desc=input_file)
            for _ in input_file_handle:
                pass


if __name__ == '__main__':
    main()
