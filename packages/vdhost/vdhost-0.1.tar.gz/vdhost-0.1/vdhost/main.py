import click

from vdhost.cli.setcommands import setcommands
from vdhost.cli.mine import mine
from vdhost.cli.stop import stop


@click.group()
def cli():
    """
    Vectordash vdhost interacts allows hosts to have auto-mining capabilities and execute their desired
    mining commands.
    More help is available under each command listed below.
    """
    pass


def add_commands(cli):
    cli.add_command(setcommands)
    cli.add_command(mine)
    cli.add_command(stop)


add_commands(cli)
