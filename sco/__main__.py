#!/usr/bin/env python3

# Wrapper over Uvicorn, to grab uvicorn logging level

from logging import Logger
from typing import Dict, Union

import click
import uvicorn
from click_help_colors import HelpColorsCommand

from .common.logging import configure_logbook


LOG_LEVELS = {
    1: 'info',
    2: 'debug',
}


@click.command(cls=HelpColorsCommand, help_options_color='yellow')  # type: ignore
@click.option('-p', '--port', default=8000)
@click.option('--host', default='127.0.0.1')
@click.option('--uds',)
@click.option('--reload', is_flag=True)
@click.option('-v', '--verbose', count=True, help='Show more log to debug (verbose mode).')
@click.option('-lc', '--limit-concurrency', default=10, help='Limit the number of coming requests')
def main(port: int, host: str, uds: str, reload: bool, verbose: int, limit_concurrency: int):
    # TODO: "reload" will make our logging config lost, because
    # then Uvicorn will create another process to do actual web server job.
    options: Dict[str, Union[bool, str, int]] = {
        'reload': reload,
        'limit_concurrency': limit_concurrency
    }
    if not uds:
        options['port'] = port
        options['host'] = host
    else:
        options['uds'] = uds
    configure_logbook(verbose)
    # Configure log level for uvicorn
    if verbose:
        lv = max(verbose, len(LOG_LEVELS.keys()))
        options['log_level'] = LOG_LEVELS[lv]
    else:
        options['log_level'] = 'warning'
    uvicorn.run('sco.main:app', **options)


if __name__ == '__main__':
    main()
