import click

from vdhost.cli.install import install
from vdhost.cli.launch import launch
from vdhost.cli.login import login
from vdhost.cli.set_commands import set_commands
from vdhost.cli.set_gpu_ids import set_gpu_ids
from vdhost.cli.start_miner import start_miner
from vdhost.cli.stop_miner import stop_miner


@click.group()
def cli():
    """
    Allows hosts to list their GPUs on Vectordash and
    gives the option of auto-switching to a miner.

    More help is available under each command listed below.
    """
    pass


def add_commands(cli):
    cli.add_command(install)
    cli.add_command(launch)
    cli.add_command(login)
    cli.add_command(set_commands)
    cli.add_command(set_gpu_ids)
    cli.add_command(start_miner)
    cli.add_command(stop_miner)


add_commands(cli)
