import logging

import click
import docker

from beautifultable import BeautifulTable

from opx import workspace

L = logging.getLogger('opx')


@click.command()
def status() -> None:
    """Show overview of workspaces.

    Lists workspace directory, container image, and container name.
    """
    table = BeautifulTable()
    table.left_border_char = ''
    table.right_border_char = ''
    table.top_border_char = ''
    table.bottom_border_char = ''
    # yes, separator is spelled incorrectly in the library
    table.row_separator_char = ''
    table.header_separator_char = ''
    table.column_headers = ['workspace', 'image', 'container']
    table.column_alignments['workspace'] = BeautifulTable.ALIGN_LEFT
    table.column_alignments['image'] = BeautifulTable.ALIGN_LEFT
    table.column_alignments['container'] = BeautifulTable.ALIGN_LEFT

    parser = workspace.parser_read()
    client = docker.from_env()

    for root in parser.sections():
        row = [root, '', '']
        if parser[root].get('cid', '') != '':
            container = client.containers.get(parser[str(root)].get('cid'))
            row[1] = container.image.short_id
            row[2] = container.name
        table.append_row(row)

    L.info(table)
