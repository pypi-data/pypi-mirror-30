import click

from vdhost.cli.set_commands import set_commands
from vdhost.cli.mine import mine
from vdhost.cli.stop_miner import stop_miner
from vdhost.cli.set_gpu_ids import set_gpu_ids
from vdhost.cli.launch import launch


@click.group()
def cli():
    """
    Allows hosts to list their GPUs on Vectordash and
    gives the option of auto-switching to a miner.

    More help is available under each command listed below.
    """
    pass


def add_commands(cli):
    cli.add_command(set_commands)
    cli.add_command(mine)
    cli.add_command(stop_miner)
    cli.add_command(set_gpu_ids)
    cli.add_command(launch)


add_commands(cli)
