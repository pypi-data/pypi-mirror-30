import click
import os
from colored import fg
from colored import stylize


@click.command(name='login')
def login():
    """
    args: none |
    Allows host to login on machine to be hosted

    """
    try:
        dot_folder = os.path.expanduser('~/.vectordash/')
        if not os.path.isdir(dot_folder):
            os.mkdir(dot_folder)
            print(stylize("Created " + dot_folder, fg("green")))

        # Save ids to gpu_ids file
        login_file = dot_folder + 'login'

        print(stylize("Email address: ", fg("blue")))
        email = input()
        print(stylize("Machine key: ", fg("blue")))
        machine_key = input()

        f = open(login_file, 'w')
        f.write(str(email))
        f.write(str(machine_key))
        f.close()

        print(stylize("Saved login information", fg("green")))
        print("If you have already ran " + stylize("vdhost install", fg("blue")) +
              " successfully, you can now list your machine on Vectordash by running " +
              stylize("vdhost launch", fg("blue")))

    except Exception as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))
