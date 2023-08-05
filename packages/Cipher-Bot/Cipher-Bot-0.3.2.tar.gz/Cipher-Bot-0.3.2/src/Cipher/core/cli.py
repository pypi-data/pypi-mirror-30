import subprocess
import sys

import click

from Cipher import __version__
from Cipher.core import CipherCore


@click.command()
@click.version_option(version=__version__)
@click.option('--debug/--no-debug', '-d', default=False)
@click.argument('config_path', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def main(config_path, debug):
    core = CipherCore(config_path, debug=debug)
    core.startup()
    if core.restarting:
        subprocess.Popen(sys.argv)
