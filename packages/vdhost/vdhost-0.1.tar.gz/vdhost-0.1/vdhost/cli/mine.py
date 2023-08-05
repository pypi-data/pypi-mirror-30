import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command()
def mine():
    """
    args: None
    Prompt user to set up commands for mining on their machine

    """
    try:
        mining_path = os.path.expanduser('~/.vectordash/mining/mine.sh')
        pid_path = os.path.expanduser('~/.vectordash/mining/pid')

        if os.path.exists(mining_path):
            subprocess.call("chmod +x " + mining_path, shell=True)
            p = subprocess.Popen(mining_path)

            # write pid to file
            f = open(pid_path, 'w')
            f.write(str(p.pid))
            f.close()

        else:
            print("Please run " + stylize("vdhost set-commands", fg("blue")) + " before trying to mine.")

    except Exception as e:
        print(stylize("The following error was thrown: ", fg("red")) + str(e))
        print(stylize("Your mining commands could not be executed. Are you sure you are using absolute paths?",
                      fg("red")))

