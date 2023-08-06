import os
import sys
import argparse
sys.path.insert(0, os.getcwd())
import forgit

# Commandline interface
parser = argparse.ArgumentParser()



parser.add_argument("-k", "--kind",
                    type=str,
                    help=None,
                    nargs="?",
                    default=".gitignore")


parser.add_argument("-d", "--dest",
                    type=str,
                    help="",
                    default=None,
                    nargs="?")

# parser.add_argument("-n", "--new",
#                     action='store_true')
#
#
# parser.add_argument("-u", "--update",
#                     action='store_true')

args = parser.parse_args()

def main():
    # print(vars(args)["new"])
    # args = vars(args)
    forgit.utils.github_tools.grab(**vars(args))
