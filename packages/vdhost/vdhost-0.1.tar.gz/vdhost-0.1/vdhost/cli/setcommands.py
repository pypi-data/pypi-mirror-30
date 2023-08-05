import click
import os
from colored import fg
from colored import stylize


@click.command()
def setcommands():
    """
    args: None
    Prompt user to set up commands for mining on their machine

    """
    try:
        dot_folder = os.path.expanduser('~/.vectordash')
        mining_folder = os.path.expanduser('~/.vectordash/mining')
        if not os.path.isdir(dot_folder):
            os.mkdir(dot_folder)
            os.mkdir(mining_folder)
            print(stylize("Created " + dot_folder, fg("green")))
            print(stylize("Created " + mining_folder, fg("green")))

        elif not os.path.isdir(mining_folder):
            os.mkdir(mining_folder)
            print(stylize("Created " + mining_folder, fg("green")))

        commands = []

        # get commands from user
        cmd = input(stylize("Please enter the commands you use to start your miner, line by line.\n"
                            "Make sure that all paths provided are absolute paths\n"
                    "Once you are done, do not type anything and press Enter twice:\n\n", fg("green")))
        commands.append(cmd)

        while 1:
            cmd = input("")
            if cmd == '':
                break
            commands.append(cmd)

        # Save commands to mining file
        mine_file = mining_folder + '/mine.sh'
        f = open(mine_file, 'w+')
        f.write("#!/usr/bin/env bash\n")
        for cmd in commands:
            f.write(cmd)
            f.write('\n')
        f.close()

        # Mining process is NOT running, so give pid file a value of -1
        pid_file = mining_folder + '/pid'
        f = open(pid_file, 'w+')
        f.write('-1')
        f.close()

    except Exception as e:
        print(stylize("The following error was thrown: ", fg("red")) + str(e))
