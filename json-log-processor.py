from __future__ import (absolute_import, division, print_function)

import json


def main():
    commits = None
    print("Now loading JSON file...")
    with open("next-parsed.json", "r") as fp:
        commits = json.load(fp)
    print("Finished loading JSON file.")


if __name__ == '__main__':
    main()