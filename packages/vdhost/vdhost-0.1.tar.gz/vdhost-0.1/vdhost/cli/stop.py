import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command()
def stop():
    """
    args: None
    Prompt user to set up commands for mining on their machine

    """
    try:

        pid_path = os.path.expanduser('~/.vectordash/mining/pid')

        if os.path.exists(pid_path):
            f = open(pid_path, 'r')
            p = f.read()
            f.close()

            if int(p) < 0:
                return

            # kill the process with process id pid
            subprocess.call("kill -- -$(ps -o pgid= " + p + " | grep -o [0-9]*)", shell=True)
            # subprocess.call("kill " + p, shell=True)

            while pid_exists(p):
                print("Attempting to force kill subprocess")
                subprocess.call("kill -9 -p " + p, shell=True)

            # write -1 to pid file
            f = open(pid_path, 'w')
            f.write("-1")
            f.close()

        else:
            print("Please run " + stylize("vdhost mine", fg("blue")) + " before trying to stop mining.")
            return
  
    except ValueError as e:
        print(stylize("The following error was thrown: ", fg("red")) + str(e))
        print(stylize("Your mining commands could not be executed. Are you sure you are using absolute paths?",
                      fg("red")))


def pid_exists(pid):
    """Check whether pid exists in the current process table.
    UNIX only.
    """
    try:
        print("Double-checking to ensure process was killed")
        os.kill(int(pid), 0)
    except OSError:
        print("pid: " + pid + " killed")
        return False
    else:
        print("pid: " + pid + " still exists")
        return True

