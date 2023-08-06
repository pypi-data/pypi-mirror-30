import click
import subprocess
import os

from colored import fg
from colored import stylize


@click.command()
def launch():
    """
    args: None |
    Runs the client Daemon on the host's machine (IN PROD)

    """
    try:
        print(stylize("Launching the Vectordash client on this machine", fg("green")))

        var_folder = os.path.expanduser('/var/')
        var_vd_folder = os.path.expanduser(var_folder + 'vectordash/')
        if not os.path.isdir(var_folder) or not os.path.isdir(var_vd_folder):
            os.mkdir(var_folder)
            print(stylize("Could not launch", fg("red")))
            print("Are you sure have run: ", stylize("vdhost install", fg("blue")))
            print("If not, please navigate to the vectordash-host directory and run that command")
            exit()

        client_py = os.path.expanduser(var_vd_folder + 'client.py')
        sshtunnel_py = os.path.expanduser(var_vd_folder + 'SSHtunnel.py')
        networkingprotocol_py = os.path.expanduser(var_vd_folder + 'NetworkingProtocol.py')
        specs_py = os.path.expanduser(var_vd_folder + 'specs.py')
        containercontroller_py = os.path.expanduser(var_vd_folder + 'ContainerController.py')

        if not os.path.exists(client_py) or not os.path.exists(sshtunnel_py) or not os.path.exists(specs_py) or \
                not os.path.exists(networkingprotocol_py) or not os.path.exists(containercontroller_py):
            print(stylize("It seems as though you have not downloaded one or more the following files:", fg("red")))

            print(stylize(client_py, fg("blue")))
            print(stylize(sshtunnel_py, fg("blue")))
            print(stylize(networkingprotocol_py, fg("blue")))
            print(stylize(specs_py, fg("blue")))
            print(stylize(containercontroller_py, fg("blue")))

            print(stylize("Please go to vectordash.com to download them and make sure they are stored in the "
                          "appropriate directory: " + var_vd_folder,
                          fg("red")))
            exit()
        else:
            subprocess.call("python3 " + client_py, shell=True)


    except ValueError as e:
        print(stylize("The following error was thrown: ", fg("red")) + str(e))
        print(stylize("The Vectordash client could not be launched. Please make a github pull request with your error.",
                      fg("red")))
