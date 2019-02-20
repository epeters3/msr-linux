from __future__ import (absolute_import, division, print_function)

import json


def main():
    commits = None
    print("Now loading JSON file...")
    with open("next-parsed.json", "r") as fp:
        commits = json.load(fp)
    print("JSON data loaded. Now re-writing...")
    with open("next-parsed.json", "w") as fp:
        json.dump(commits, fp, separators=(',', ':'), default=str)
    print("Finished.")


if __name__ == '__main__':
    main()