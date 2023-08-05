import os

import sys

from clinodes.nodes import ArgNode

import gofri.lib.project_generator.generator as G

if __name__ == '__main__':
    args = sys.argv[1::]
    length = len(args)

    if length > 0:
        if length == 1:
            proj_name = sys.argv[1]
            print("Generating project '{}'".format(proj_name))
            G.generate_project(os.getcwd(), proj_name)
        elif length == 2:
            if sys.argv[2] == "-v" or sys.argv[2] == "--venv":
                proj_name = sys.argv[1]
                print("Project(virtualenv) '{}'".format(proj_name))
                G.generate_project(os.getcwd(), proj_name, use_venv=True)
            else:
                raise Exception("Invalid option {}".format(sys.argv[2]))
        else:
            raise Exception("Too much args")
    else:
        raise Exception("Specify project name!")