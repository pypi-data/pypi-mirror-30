import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command(name='stop-miner')
def stop_miner():
    """
    args: None |
    Prompt user to set up commands for mining on their machine

    """
    try:

        pid_path = os.path.expanduser('~/.vectordash/mining/pid')

        if os.path.exists(pid_path):
            print("Stopping the mining process now...")
            f = open(pid_path, 'r')
            p = f.read()
            f.close()

            if int(p) < 0:
                print("Not currently mining. Run " + stylize("vdhost mine", fg("blue")) + " to start mining")
                return

            # kill the process with process id pid
            subprocess.call("kill -- -$(ps -o pgid= " + p + " | grep -o [0-9]*)", shell=True)

            while pid_exists(p):
                print("Attempting to stop mining")
                subprocess.call("kill -9 -p " + p, shell=True)

            # write -1 to pid file
            f = open(pid_path, 'w')
            f.write("-1")
            f.close()

        else:
            print("Please run " + stylize("vdhost mine", fg("blue")) + " before trying to stop mining.")
            return
  
    except ValueError as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))
        print(stylize("Your mining commands could not be executed. Are you sure you are using absolute paths?",
                      fg("red")))


def pid_exists(pid):
    """
    Check whether pid exists in the current process table.
    """
    try:
        print("Double-checking to ensure mining was stoped")
        os.kill(int(pid), 0)
    except OSError:
        print("pid: " + pid + " killed")
        return False
    else:
        print("pid: " + pid + " still exists")
        return True

