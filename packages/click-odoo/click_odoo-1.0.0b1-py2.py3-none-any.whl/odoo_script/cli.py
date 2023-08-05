# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import runpy
import sys

import click

from .console import interact
from .env import OdooEnvironment

_logger = logging.getLogger(__name__)


@click.command(help="Execute a python script in an initialized Odoo "
                    "environment. The script has access to a 'env' global "
                    "variable which is the odoo.api.Environment initialized "
                    "for the given database. If no script is provided, "
                    "the script is read from stdin or an interactive console "
                    "is started if stdin appears to be a terminal.")
@click.option('--config', '-c', envvar=['ODOO_RC', 'OPENERP_SERVER'],
              type=click.Path(exists=True, dir_okay=False),
              help="Specify the Odoo configuration file. Other "
                   "ways to provide it are with the ODOO_RC or "
                   "OPENERP_SERVER environment variables, or ~/.odoorc "
                   "(Odoo >= 10) or ~/.openerp_serverrc.")
@click.option('--database', '-d', envvar=['PGDATABASE'],
              help="Specify the database name.")
@click.option('--log-level',
              help="Specify the logging level. Accepted values depend on the "
                   "Odoo version, and include debug, info (default), warn, "
                   "error.")
@click.option('--interactive/--no-interactive', '-i',
              help="Inspect interactively after running the script.")
@click.option('--shell-interface',
              help="Preferred shell interface for interactive mode. Accepted "
                   "values are ipython, ptpython, bpython, python. If not "
                   "provided they are tried in this order.")
@click.argument('script', required=False,
                type=click.Path(exists=True, dir_okay=False))
@click.argument('script-args', nargs=-1)
def main(config, database, log_level, interactive, shell_interface,
         script, script_args):
    with OdooEnvironment(
        config=config,
        database=database,
        log_level=log_level,
    ) as env:
        global_vars = {'env': env}
        if script:
            sys.argv[1:] = script_args
            global_vars = runpy.run_path(script, init_globals=global_vars)
        if not script or interactive:
            interact(global_vars, shell_interface, interactive)
