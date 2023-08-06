import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command()
def install():
    """
    args: None |
    Runs the install process on the host machine to configure it with ML libraries
    and any other dependencies

    """
    try:
        print(stylize("Launching the Vectordash installation process on this machine", fg("green")))
        print(stylize("When prompted with any questions, please hit ENTER for default values", fg("green")))

        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')
        if not os.path.isdir(var_folder):
            os.mkdir(var_folder)
            print(stylize("Created " + var_folder, fg("green")))

        if not os.path.isdir(var_vd_folder):
            os.mkdir(var_vd_folder)
            print(stylize("Created " + var_vd_folder, fg("green")))

        install_script = os.path.expanduser('./install.sh')
        requirements = os.path.expanduser('./requirements.txt')
        if not os.path.exists(install_script):
            print(stylize("You are missing one or more of the following files:", fg("red")))

            print(stylize(install_script, fg("blue")))
            print(stylize(requirements, fg("blue")))

            print("Please go to https://vectordash.com/ to download the missing files")

        else:
            subprocess.call("bash " + install_script, shell=True)

    except ValueError as e:
        print(stylize("The following error was thrown: ", fg("red")) + str(e))
        print(stylize("The Vectordash client could not be launched. Please make a github pull request with your error.",
                      fg("red")))
