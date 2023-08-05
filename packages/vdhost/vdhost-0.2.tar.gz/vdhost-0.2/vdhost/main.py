import click

from vdhost.cli.setcommands import setcommands
from vdhost.cli.mine import mine
from vdhost.cli.stop import stop
from vdhost.cli.set_gpu_ids import set_gpu_ids


@click.group()
def cli():
    """
    Allows hosts to list their GPUs on Vectordash and
    gives the option of auto-switching to a miner.

    More help is available under each command listed below.
    """
    pass


def add_commands(cli):
    cli.add_command(setcommands)
    cli.add_command(mine)
    cli.add_command(stop)
    cli.add_command(set_gpu_ids)


add_commands(cli)
