import click
import os
from colored import fg
from colored import stylize


@click.command()
@click.argument('gpu_ids', required=True, nargs=-1)
def set_gpu_ids(gpu_ids):
    """
    args: gpu_ids
    Allow user to select the GPUs they would like to rent out on Vectordash

    """
    try:
        dot_folder = os.path.expanduser('~/.vectordash')
        if not os.path.isdir(dot_folder):
            os.mkdir(dot_folder)
            print(stylize("Created " + dot_folder, fg("green")))

        # Save commands to mining file
        gpu_ids_file = dot_folder + '/gpu_ids'

        temp = str(gpu_ids)
        temp1 = temp.replace('(', '')
        temp2 = temp1.replace(')', '')
        temp3 = temp2.replace(',', '')
        final_ids = temp3.replace('\'', '')

        f = open(gpu_ids_file, 'w')
        f.write(str(final_ids))
        f.close()

        print(stylize("Saved GPU IDs to " + gpu_ids_file, fg("green")))

    except Exception as e:
        print(stylize("The following error was thrown: ", fg("red")) + str(e))
